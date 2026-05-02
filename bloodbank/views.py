from django.shortcuts import render, redirect, get_object_or_404







from django.contrib.auth import login, authenticate, logout







from django.contrib.auth.decorators import login_required







from django.contrib.auth.mixins import LoginRequiredMixin







from django.contrib import messages







from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView







from django.urls import reverse_lazy







from django.db.models import Count, Q, Sum







from django.utils import timezone







from django.core.exceptions import PermissionDenied







from .models import User, BloodRequest, BloodStock, Donation, Notification
from .utils import send_notification_email







from .forms import CustomUserCreationForm, BloodRequestForm, BloodStockForm, DonationForm, DonorBloodRequestForm, ProfileForm







from .views_custom import custom_logout







from .decorators import admin_required, donor_required, patient_required, validate_object_access, validate_blood_request_status, validate_blood_stock





def create_notification(user, title, message, notification_type='general', link=None):

    """Helper function to create a new notification for a user"""

    return Notification.objects.create(

        user=user,

        title=title,

        message=message,

        notification_type=notification_type,

        link=link

    )







def update_donation_status():

    """Update donation status from 'scheduled' to 'completed' when patient's required date has passed"""

    today = timezone.now().date()

    # Update donations where the patient's required date has passed (today or before)

    scheduled_donations = Donation.objects.filter(

        status='scheduled', 

        blood_request__required_date__lte=today

    )

    updated_count = scheduled_donations.update(status='completed')

    return updated_count









def home(request):
    # Redirect authenticated users away from home page based on their role
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('dashboard')  # Admin goes to dashboard
        elif hasattr(request.user, 'role'):
            if request.user.role == 'patient':
                return redirect('dashboard')  # Patient goes to dashboard
            elif request.user.role == 'donor':
                return redirect('dashboard')  # Donor goes to dashboard
    
    # Show the home page only for non-authenticated users
    from .models import BloodStock
    
    # Get blood stock data for blood types section
    blood_stocks = BloodStock.objects.all().order_by('blood_group')
    
    context = {
        'page_title': 'Home - LifeServe Blood Bank',
        'blood_stocks': blood_stocks,
    }
    
    return render(request, 'bloodbank/home_modern.html', context)














def register(request):







    if request.method == 'POST':







        form = CustomUserCreationForm(request.POST)







        if form.is_valid():







            user = form.save()







            username = form.cleaned_data.get('username')







            messages.success(request, f'Account created for {username}')







            return redirect('login')







    else:







        form = CustomUserCreationForm()







    return render(request, 'bloodbank/register_modern.html', {'form': form})















@login_required







def dashboard(request):







    user = request.user







    context = {}







    







    if user.role == 'admin':







        context.update({







            'total_users': User.objects.count(),







            'total_patients': User.objects.filter(role='patient').count(),







            'total_donors': User.objects.filter(role='donor').count(),







            'total_requests': BloodRequest.objects.count(),







            'pending_requests': BloodRequest.objects.filter(status='pending').count(),







            'approved_requests': BloodRequest.objects.filter(status='approved').count(),







            'fulfilled_requests': BloodRequest.objects.filter(status='fulfilled').count(),







            'blood_stocks': BloodStock.objects.all(),







            'recent_requests': BloodRequest.objects.order_by('-requested_date')[:5],







        })







    elif user.role == 'patient':







        context.update({







            'my_requests': BloodRequest.objects.filter(patient=user).order_by('-requested_date'),







            'pending_requests': BloodRequest.objects.filter(patient=user, status='pending').count(),







            'approved_requests': BloodRequest.objects.filter(patient=user, status='approved').count(),







            'fulfilled_requests': BloodRequest.objects.filter(patient=user, status='fulfilled').count(),







        })





    elif user.role == 'donor':


        # Auto-update donation status from scheduled to completed
        update_donation_status()


        # Get current date for proper filtering
        today = timezone.now().date()


        # Only show requests to verified donors
        if user.is_verified:
            available_requests = BloodRequest.objects.filter(
                status='approved',
                blood_group=user.blood_group,
                required_date__gte=today  # Only show requests with future dates
            ).order_by('-requested_date')
        else:
            available_requests = BloodRequest.objects.none()  # Empty queryset for unverified donors


        context.update({
            'available_requests': available_requests,
            'my_donations': Donation.objects.filter(donor=user).order_by('-created_at'),
            'completed_donations': Donation.objects.filter(donor=user, status='completed').count(),
        })



    







    return render(request, f'bloodbank/dashboard_{user.role}.html', context)















class BloodRequestCreateView(LoginRequiredMixin, CreateView):







    model = BloodRequest







    form_class = BloodRequestForm







    template_name = 'bloodbank/request_blood.html'







    success_url = reverse_lazy('dashboard')







    







    def get_form_class(self):







        # Use different form for donors







        if self.request.user.role == 'donor':







            return DonorBloodRequestForm







        return BloodRequestForm







    







    def form_valid(self, form):







        # Allow patients and donors to create requests







        if self.request.user.role in ['patient', 'donor']:







            if self.request.user.role == 'patient':







                form.instance.patient = self.request.user







            else:  # Donor creating request for themselves (should be assigned to a patient)







                # Don't set patient field for donors







                pass







            messages.success(self.request, 'Blood request submitted successfully!')

            

            response = super().form_valid(form)

            

            # Notify all admins

            admins = User.objects.filter(role='admin')

            for admin in admins:

                create_notification(

                    user=admin,

                    title="New Blood Request",

                    message=f"A new request for {form.instance.blood_group} has been submitted by {self.request.user.username}.",

                    notification_type='request_created',

                    link=reverse_lazy('request_list')

                )
            
            admin_emails = [admin.email for admin in admins if admin.email]
            if admin_emails:
                send_notification_email(
                    subject="New Blood Request Submitted",
                    message=f"A new request for {form.instance.blood_group} has been submitted by {self.request.user.username}.",
                    recipient_list=admin_emails
                )

            return response







        else:







            messages.error(self.request, 'Only patients and donors can create blood requests.')







            return redirect('dashboard')















class BloodRequestListView(LoginRequiredMixin, ListView):







    model = BloodRequest







    template_name = 'bloodbank/request_list.html'







    context_object_name = 'requests'







    paginate_by = 10







    







    def get_queryset(self):







        user = self.request.user







        base_queryset = BloodRequest.objects.all().order_by('-requested_date')







        







        # Apply filters based on user role







        if user.role == 'admin':







            queryset = base_queryset







        elif user.role == 'patient':







            queryset = base_queryset.filter(patient=user)







        elif user.role == 'donor':







            queryset = base_queryset.filter(







                blood_group=user.blood_group,







                status='pending'







            )







        else:







            queryset = BloodRequest.objects.none()







        



        # Apply GET parameter filters
        status_filter = self.request.GET.get('status', '')
        urgency_filter = self.request.GET.get('urgency', '')
        blood_group_filter = self.request.GET.get('blood_group', '')
        search_query = self.request.GET.get('search', '')
        date_filter = self.request.GET.get('date', '')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if urgency_filter:
            queryset = queryset.filter(urgency=urgency_filter)

        if blood_group_filter:
            queryset = queryset.filter(blood_group=blood_group_filter)

        if date_filter:
            queryset = queryset.filter(requested_date__date=date_filter)

        # Add search functionality
        if search_query:
            queryset = queryset.filter(
                Q(patient__username__icontains=search_query) |
                Q(hospital_name__icontains=search_query) |
                Q(doctor_name__icontains=search_query) |
                Q(blood_group__icontains=search_query) |
                Q(reason__icontains=search_query)
            )

        return queryset













@admin_required







def approve_request(request, pk):







    blood_request = get_object_or_404(BloodRequest, pk=pk)







    







    # Validate object access







    access_valid, access_message = validate_object_access(request.user, blood_request, 'approve')







    if not access_valid:







        messages.error(request, access_message)







        return redirect('dashboard')







    







    # Validate status transition







    status_valid, status_message = validate_blood_request_status(request, blood_request, 'approved')







    if not status_valid:







        messages.error(request, status_message)







        return redirect('dashboard')







    







    # Additional validation: check if request is pending







    if blood_request.status != 'pending':







        messages.error(request, 'Only pending requests can be approved.')







        return redirect('dashboard')







    







    # Validate blood stock availability







    stock_valid, stock_result = validate_blood_stock(blood_request.blood_group, blood_request.units_required)







    if not stock_valid:







        messages.warning(request, f'Low stock warning: {stock_result}. Consider requesting more donations.')







    







    blood_request.status = 'approved'







    blood_request.approved_date = timezone.now()







    blood_request.save()

    

    # Notify the patient

    if blood_request.patient:

        create_notification(

            user=blood_request.patient,

            title="Blood Request Approved",

            message=f"Your request for {blood_request.blood_group} has been approved by an administrator.",

            notification_type='request_approved',

            link='/dashboard/'

        )

    

    # Notify all matching donors

    matching_donors = User.objects.filter(role='donor', blood_group=blood_request.blood_group)

    for donor in matching_donors:

        create_notification(

            user=donor,

            title="Blood Needed!",

            message=f"A request for your blood group ({blood_request.blood_group}) has been approved. Please consider donating.",

            notification_type='donor_matching_request',

            link='/dashboard/'

        )



    messages.success(request, f'Request #{blood_request.id} has been approved.')







    







    return redirect('dashboard')















@admin_required







def fulfill_request(request, pk):







    blood_request = get_object_or_404(BloodRequest, pk=pk)







    







    # Validate object access







    access_valid, access_message = validate_object_access(request.user, blood_request, 'fulfill')







    if not access_valid:







        messages.error(request, access_message)







        return redirect('dashboard')







    







    # Validate status transition







    status_valid, status_message = validate_blood_request_status(request, blood_request, 'fulfilled')







    if not status_valid:







        messages.error(request, status_message)







        return redirect('dashboard')







    







    # Additional validation: check if request is approved







    if blood_request.status != 'approved':







        messages.error(request, 'Only approved requests can be fulfilled.')







        return redirect('dashboard')







    







    # Validate blood stock availability







    stock_valid, stock_result = validate_blood_stock(blood_request.blood_group, blood_request.units_required)







    if not stock_valid:







        messages.error(request, f'Insufficient blood stock for {blood_request.blood_group}. {stock_result}')







        return redirect('dashboard')







    







    # Update blood stock







    blood_stock = stock_result







    blood_stock.units -= blood_request.units_required







    blood_stock.save()







    







    blood_request.status = 'fulfilled'







    blood_request.fulfilled_date = timezone.now()

    blood_request.save()

    

    # Notify the patient

    if blood_request.patient:

        create_notification(

            user=blood_request.patient,

            title="Blood Request Fulfilled",

            message=f"Your request for {blood_request.blood_group} has been marked as fulfilled. We hope you are doing well.",

            notification_type='request_fulfilled',

            link='/dashboard/'

        )







    







    messages.success(request, f'Request #{blood_request.id} has been fulfilled. {blood_request.units_required} units of {blood_request.blood_group} deducted from stock.')







    return redirect('dashboard')















@donor_required







def accept_donation(request, pk):







    blood_request = get_object_or_404(BloodRequest, pk=pk)







    







    # Validate object access







    access_valid, access_message = validate_object_access(request.user, blood_request, 'accept')







    if not access_valid:







        messages.error(request, access_message)







        return redirect('dashboard')







    







    # Additional validation: check if request is approved and not assigned







    if blood_request.status != 'approved':







        messages.error(request, 'Only approved requests can be accepted for donation.')







        return redirect('dashboard')







    







    if blood_request.assigned_donor:







        messages.error(request, 'This request has already been assigned to a donor.')







        return redirect('dashboard')







    







    # Validate donor blood group matches







    if request.user.blood_group != blood_request.blood_group:







        messages.error(request, f'Your blood group ({request.user.blood_group}) does not match the required blood group ({blood_request.blood_group}).')







        return redirect('dashboard')







    







    # Validate donor is verified







    if not request.user.is_verified:







        messages.error(request, 'You must be verified to accept donation requests.')







        return redirect('dashboard')







    







    blood_request.assigned_donor = request.user







    blood_request.status = 'fulfilled'  # Changed to fulfilled when donation is accepted







    blood_request.fulfilled_date = timezone.now()







    blood_request.save()







    







    # Create donation record with initial 'scheduled' status

    Donation.objects.create(

        donor=request.user,

        blood_request=blood_request,

        donation_date=timezone.now(),

        status='scheduled',  # Initial status should be 'scheduled'

        units_donated=blood_request.units_required

    )





    messages.success(request, f'You have accepted donation request #{blood_request.id}. Please prepare for donation.')

    

    # Notify the patient

    if blood_request.patient:

        create_notification(

            user=blood_request.patient,

            title="Donor Found!",

            message=f"Donor {request.user.username} has accepted your request for {blood_request.blood_group} and scheduled a donation.",

            notification_type='donation_accepted',

            link='/dashboard/'

        )

    

    # Notify all admins

    admins = User.objects.filter(role='admin')

    for admin in admins:

        create_notification(

            user=admin,

            title="Donation Scheduled",

            message=f"Donor {request.user.username} has scheduled a donation for Request #{blood_request.id}.",

            notification_type='donation_scheduled',

            link='/requests/'

        )

    if blood_request.patient and blood_request.patient.email:
        send_notification_email(
            subject="Donor Found!",
            message=f"Donor {request.user.username} has accepted your request for {blood_request.blood_group} and scheduled a donation.",
            recipient_list=[blood_request.patient.email]
        )

    admin_emails = [admin.email for admin in admins if admin.email]
    if admin_emails:
        send_notification_email(
            subject="Donation Scheduled",
            message=f"Donor {request.user.username} has scheduled a donation for Request #{blood_request.id}.",
            recipient_list=admin_emails
        )

    return redirect('dashboard')















@login_required

@donor_required

def cancel_donation(request, pk):

    """

    Handle donor cancelling a scheduled donation.

    Only allows cancellation of donations with 'scheduled' status.

    """

    donation = get_object_or_404(Donation, pk=pk)

    

    # Validate object access

    access_valid, access_message = validate_object_access(request.user, donation, 'cancel')



    if not access_valid:

        messages.error(request, access_message)

        return redirect('dashboard')

    

    # Only allow cancellation of scheduled donations

    if donation.status != 'scheduled':

        messages.error(request, 'Only scheduled donations can be cancelled.')

        return redirect('dashboard')

    

    # Update donation status to cancelled

    donation.status = 'cancelled'

    donation.save()

    

    # Update blood request to make it available again

    blood_request = donation.blood_request

    blood_request.assigned_donor = None

    blood_request.status = 'approved'  # Make request available again

    blood_request.save()

    

    messages.success(request, f'Your scheduled donation for request #{blood_request.id} has been cancelled.')

    

    # Notify the patient

    if blood_request.patient:

        create_notification(

            user=blood_request.patient,

            title="Scheduled Donation Cancelled",

            message=f"The donor who scheduled a donation for your request #{blood_request.id} has cancelled. Your request is now available for other donors.",

            notification_type='donation_cancelled',

            link='/dashboard/'

        )

    

    # Notify all admins

    admins = User.objects.filter(role='admin')

    for admin in admins:

        create_notification(

            user=admin,

            title="Scheduled Donation Cancelled",

            message=f"Donor {request.user.username} has cancelled their scheduled donation for Request #{blood_request.id}.",

            notification_type='donation_cancelled',

            link='/requests/'

        )

    if blood_request.patient and blood_request.patient.email:
        send_notification_email(
            subject="Scheduled Donation Cancelled",
            message=f"The donor who scheduled a donation for your request #{blood_request.id} has cancelled. Your request is now available for other donors.",
            recipient_list=[blood_request.patient.email]
        )

    admin_emails = [admin.email for admin in admins if admin.email]
    if admin_emails:
        send_notification_email(
            subject="Scheduled Donation Cancelled",
            message=f"Donor {request.user.username} has cancelled their scheduled donation for Request #{blood_request.id}.",
            recipient_list=admin_emails
        )

    return redirect('dashboard')





class BloodStockUpdateView(LoginRequiredMixin, UpdateView):







    model = BloodStock







    form_class = BloodStockForm







    template_name = 'bloodbank/update_stock.html'







    success_url = reverse_lazy('dashboard')







    







    def dispatch(self, request, *args, **kwargs):







        if request.user.role != 'admin':







            messages.error(request, 'You do not have permission to update blood stock.')







            return redirect('dashboard')







        return super().dispatch(request, *args, **kwargs)







    







    def form_valid(self, form):







        # Validate the units value







        units = form.cleaned_data.get('units', 0)







        if units < 0:







            form.add_error('units', 'Blood stock units cannot be negative.')







            return self.form_invalid(form)







        







        if units > 10000:







            form.add_error('units', 'Blood stock units cannot exceed 10,000.')







            return self.form_invalid(form)







        







        # Log the stock update







        old_stock = BloodStock.objects.get(pk=self.object.pk).units







        new_stock = units







        change = new_stock - old_stock







        







        messages.success(self.request, f'Blood stock for {self.object.blood_group} updated from {old_stock} to {new_stock} units (change: {change:+d}).')







        return super().form_valid(form)















class UserListView(LoginRequiredMixin, ListView):







    model = User







    template_name = 'bloodbank/user_list_modern.html'







    context_object_name = 'users'







    paginate_by = 20







    







    def dispatch(self, request, *args, **kwargs):







        if not request.user.is_authenticated:







            return redirect('login')







        if not hasattr(request.user, 'role') or request.user.role != 'admin':







            messages.error(request, 'You do not have permission to view users.')







            return redirect('dashboard')







        return super().dispatch(request, *args, **kwargs)







    







    def get_queryset(self):







        # Apply filters if provided







        queryset = User.objects.all().order_by('-date_joined')







        







        role_filter = self.request.GET.get('role')







        if role_filter:







            queryset = queryset.filter(role=role_filter)







        







        verified_filter = self.request.GET.get('verified')







        if verified_filter == 'true':







            queryset = queryset.filter(is_verified=True)







        elif verified_filter == 'false':







            queryset = queryset.filter(is_verified=False)







        







        search_query = self.request.GET.get('search')







        if search_query:







            queryset = queryset.filter(







                Q(username__icontains=search_query) |







                Q(first_name__icontains=search_query) |







                Q(last_name__icontains=search_query) |







                Q(email__icontains=search_query)







            )







        







        return queryset







    







    def get_context_data(self, **kwargs):







        context = super().get_context_data(**kwargs)







        







        # Add statistics







        all_users = User.objects.all()







        context['patient_count'] = all_users.filter(role='patient').count()







        context['donor_count'] = all_users.filter(role='donor').count()







        context['verified_count'] = all_users.filter(is_verified=True).count()







        







        # Add current filters







        context['current_role'] = self.request.GET.get('role', '')







        context['current_verified'] = self.request.GET.get('verified', '')







        context['current_search'] = self.request.GET.get('search', '')







        







        return context















@admin_required







def verify_user(request, pk):







    user = get_object_or_404(User, pk=pk)







    







    # Prevent admin from unverifying themselves







    if user.pk == request.user.pk:







        messages.error(request, 'You cannot change your own verification status.')







        return redirect('user_list')







    







    # Prevent admin from unverifying other admins







    if user.role == 'admin' and user != request.user:







        messages.error(request, 'You cannot change verification status of other admin users.')







        return redirect('user_list')







    







    # Additional validation: check if user can be verified







    if user.role == 'donor' and not user.blood_group:







        messages.error(request, 'Donors must have a blood group specified before verification.')







        return redirect('user_list')







    







    # Toggle verification status







    user.is_verified = not user.is_verified







    user.save()







    







    status = 'verified' if user.is_verified else 'unverified'







    action = 'Verification granted' if user.is_verified else 'Verification revoked'







    

    

    







    messages.success(request, f'{action} for user {user.username} ({user.get_full_name()}).')







    return redirect('user_list')















@login_required







def profile(request):







    """Display user profile"""







    user = request.user







    context = {







        'user': user,







        'page_title': 'My Profile'







    }







    return render(request, 'bloodbank/profile.html', context)















@login_required







def edit_profile(request):







    """Edit user profile"""







    user = request.user







    







    if request.method == 'POST':







        form = ProfileForm(request.POST, instance=user)







        if form.is_valid():







            form.save()







            messages.success(request, 'Profile updated successfully!')







            return redirect('profile')







    else:







        form = ProfileForm(instance=user)







        # Set initial values for better UX







        form.fields['blood_group'].required = user.role == 'donor'







    







    context = {







        'form': form,







        'page_title': 'Edit Profile'







    }







    return render(request, 'bloodbank/edit_profile.html', context)





@login_required

def cancel_blood_request(request, pk):

    """Cancel a blood request - available for admin and patient (own requests only)"""

    blood_request = get_object_or_404(BloodRequest, pk=pk)

    user = request.user

    

    # Check permissions

    can_cancel = False

    cancel_reason = ""

    

    if user.role == 'admin':

        # Admin can cancel any request

        can_cancel = True

        cancel_reason = "Admin cancelled request"

    elif user.role == 'patient' and blood_request.patient == user:

        # Patient can cancel their own requests

        can_cancel = True

        cancel_reason = "Patient cancelled their request"

    

    if not can_cancel:

        messages.error(request, 'You do not have permission to cancel this blood request.')

        return redirect('dashboard')

    

    # Check if request can be cancelled (not already fulfilled or cancelled)

    if blood_request.status in ['fulfilled', 'cancelled']:

        messages.warning(request, f'This request cannot be cancelled as it is already {blood_request.get_status_display()}.')

        return redirect('dashboard')

    

    # Cancel request

    old_status = blood_request.status

    blood_request.status = 'cancelled'

    blood_request.save()

    

    # Create a note for cancellation

    if hasattr(blood_request, 'notes') and blood_request.notes:

        blood_request.notes += f"\n\nCancelled: {cancel_reason} on {timezone.now().strftime('%Y-%m-%d %H:%M')}"

    else:

        # If notes field doesn't exist, we'll just save the status change

        pass

    

    # Success message

    messages.success(request, f'Blood request #{blood_request.id} has been successfully cancelled. {cancel_reason}')

    

    # Notify patient if admin cancelled

    if request.user.role == 'admin' and blood_request.patient:

        create_notification(

            user=blood_request.patient,

            title="Blood Request Cancelled",

            message=f"Your request for {blood_request.blood_group} has been cancelled by an administrator.",

            notification_type='request_cancelled'

        )

    # Notify admins if patient cancelled

    elif request.user.role == 'patient':

        admins = User.objects.filter(role='admin')

        for admin in admins:

            create_notification(

                user=admin,

                title="Blood Request Cancelled",

                message=f"Patient {request.user.username} has cancelled their request for {blood_request.blood_group}.",

                notification_type='request_cancelled'

            )

    

    return redirect('dashboard')





def about(request):

    """Display About page with blood bank information"""

    context = {

        'page_title': 'About LifeServe Blood Bank',

        'about_info': {

            'title': 'LifeServe Blood Bank',

            'established': '2020',

            'mission': 'To save lives by providing safe, quality blood products and services to those in need.',

            'vision': 'To be the leading blood bank in the region, ensuring no life is lost due to blood shortage.',

            'services': [

                'Blood Collection & Processing',

                'Blood Component Preparation',

                'Blood Transfusion Services',

                'Emergency Blood Supply',

                'Patient Blood Management',

                'Donor Recruitment & Education'

            ],

            'statistics': {

                'total_donors': '5000+',

                'annual_collections': '10000+',

                'hospitals_served': '50+',

                'lives_saved': '25000+'

            },

            'contact_info': {

                'address': '123 Medical Center Drive, Healthcare City, HC 12345',

                'phone': '+1 (555) 123-4567',

                'email': 'info@lifeservebloodbank.com',

                'emergency_hotline': '1-800-BLOOD-HELP'

            }

        }

    }

    return render(request, 'bloodbank/about.html', context)





def contact(request):

    """Display Contact page with contact form"""

    if request.method == 'POST':

        name = request.POST.get('name', '')

        email = request.POST.get('email', '')

        subject = request.POST.get('subject', '')

        message = request.POST.get('message', '')

        

        if name and email and subject and message:

            # Here you would typically send an email

            # For now, we'll just show a success message

            messages.success(request, 'Your message has been sent successfully! We will respond within 24 hours.')

            return redirect('contact')

        else:

            messages.error(request, 'Please fill in all required fields.')

    

    context = {

        'page_title': 'Contact LifeServe Blood Bank',

        'contact_info': {

            'address': '123 Medical Center Drive, Healthcare City, HC 12345',

            'phone': '+1 (555) 123-4567',

            'email': 'info@lifeservebloodbank.com',

            'emergency_hotline': '1-800-BLOOD-HELP',

            'working_hours': 'Monday - Friday: 8:00 AM - 6:00 PM',

            'emergency_hours': '24/7 Emergency Hotline Available'

        }

    }

    return render(request, 'bloodbank/contact.html', context)





class NotificationListView(LoginRequiredMixin, ListView):

    model = Notification

    template_name = 'bloodbank/notification_list.html'

    context_object_name = 'notifications'

    paginate_by = 20



    def get_queryset(self):

        return Notification.objects.filter(user=self.request.user)





@login_required

def mark_notification_as_read(request, pk):

    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    notification.is_read = True

    notification.save()

    return redirect(request.GET.get('next', 'notification_list'))





@login_required

def mark_all_notifications_as_read(request):

    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    messages.success(request, "All notifications marked as read.")

    return redirect('notification_list')







