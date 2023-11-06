from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import PasswordChangeView,PasswordChangeDoneView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from courses.models import Course, Enrollment
from teachers.views import teacher_dashboard
from django.shortcuts import render, get_object_or_404, redirect
from .forms import DiscussionForm, ReplyForm
from .models import Discussion, Reply
from django.core.exceptions import PermissionDenied


@login_required
def dashboard(request):
    if request.user.user_type == 'student':
        return student_dashboard(request)
    elif request.user.user_type == 'teacher':
        return teacher_dashboard(request)

def student_dashboard(request):
    # Retrieve the courses the student is enrolled in
    courses = Course.objects.filter(students=request.user)
    return render(request, 'students/student_dashboard.html', {'courses': courses})


def homepage(request):
    return render(request, 'homepage.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')



def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registration

            # Assign the user to the "Default" group
            default_group, _ = Group.objects.get_or_create(name='Default')
            user.groups.add(default_group)

            return redirect('dashboard')  # Redirect to the dashboard or any other desired page
    else:
        form = UserRegistrationForm()
        print(form.errors) 
    return render(request, 'registration/register.html', {'form': form})



def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Log the user in after successful login
            return redirect('dashboard')  # Redirect to the dashboard or any other desired page
    else:
        form = AuthenticationForm()
        print(form.errors) 
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)  # Log the user out
    return redirect('login')  # Redirect to the login page


@login_required
def account_settings(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserRegistrationForm(instance=request.user)
    return render(request, 'account_settings.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change.html'  # Replace with your desired template
    success_url = reverse_lazy('password_change_done')  # URL to redirect after a successful password change

    # Customize the view as needed
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been successfully changed.')  # Display a success message
        return super().form_valid(form)
    
class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'password_change_done.html'  # Replace with your desired template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data you want to pass to the template
        return context
    
def combined_discussions(request):
    discussions = Discussion.objects.all()
    is_creating_discussion = True
    is_viewing_discussion = False
    form = None  # Initialize the form variable

    if request.method == 'POST':
    # Create a DiscussionForm instance
        form = DiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.teacher = request.user
            discussion.save()
            return redirect('combined_discussions')
        
    
        elif 'submit_reply' in request.POST:  # Button name in your reply form
            discussion_id = request.POST.get('discussion_id')
            discussion = get_object_or_404(Discussion, pk=discussion_id)
            reply_form = ReplyForm(request.POST, request.FILES)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.discussion = discussion
                reply.user = request.user
                reply.save()
                return redirect('view_discussion', discussion_id=discussion.id)

        elif 'reply_form' in request.POST:
            form = ReplyForm(request.POST)
            if form.is_valid():
                discussion_id = request.POST.get('discussion_id')
                discussion = get_object_or_404(Discussion, pk=discussion_id)
                reply = form.save(commit=False)
                reply.discussion = discussion
                reply.user = request.user
                reply.save()
                return redirect('combined_discussions')

    else:
        form = DiscussionForm()  # Initialize the form for GET requests

    # Check if the URL has a discussion_id parameter (i.e., a specific discussion is being viewed)
    if 'discussion_id' in request.GET:
        discussion_id = request.GET['discussion_id']
        discussion = get_object_or_404(Discussion, pk=discussion_id)
        replies = Reply.objects.filter(discussion=discussion)
        is_viewing_discussion = True

        context = {
            'discussions': discussions,
            'is_creating_discussion': is_creating_discussion,
            'is_viewing_discussion': is_viewing_discussion,
            'discussion_form': form,
            'reply_form': ReplyForm(),
            'discussion': discussion,  # Pass the specific discussion to the template
            'replies': replies,  # Pass the replies associated with the discussion
        }

        return render(request, 'users/templates/discussion/combined_discussions.html', context)

    context = {
        'discussions': discussions,
        'is_creating_discussion': is_creating_discussion,
        'is_viewing_discussion': is_viewing_discussion,
        'discussion_form': form,
        'reply_form': ReplyForm(),
    }

    return render(request, 'discussion/combined_discussions.html', context)


def view_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    replies = Reply.objects.filter(discussion=discussion)

    if request.method == 'POST':
        reply_form = ReplyForm(request.POST, request.FILES)
        if reply_form.is_valid():
            new_reply = reply_form.save(commit=False)
            new_reply.user = request.user
            new_reply.discussion = discussion
            new_reply.save()
            return redirect('view_discussion', discussion_id=discussion.id)
    else:
        reply_form = ReplyForm()

    # Create a context dictionary with the discussion, replies, and reply form
    context = {
        'discussion': discussion,
        'replies': replies,
        'reply_form': reply_form,
    }

    # Render the individual post detail template
    return render(request, 'discussion/post_detail.html', context)


def post_reply(request, discussion_id):
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = discussion
            reply.user = request.user  # Assuming you have a user associated
            reply.save()
            # Redirect to the discussion detail page
            return redirect('view_discussion', discussion_id=discussion.id)
    else:
        # If GET request or form not valid, render the discussion detail page with form errors
        form = ReplyForm()
    # Reuse the 'post_detail.html' template
    return render(request, 'discussion/post_detail.html', {'discussion': discussion, 'reply_form': form})

@login_required
def delete_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, pk=discussion_id)

    # Check if the current user is the teacher who created the discussion
    if discussion.teacher != request.user:
        # If not, raise a PermissionDenied exception
        raise PermissionDenied

    # If the user is the creator, delete the discussion
    discussion.delete()

    # Redirect to the discussions list page
    return redirect('combined_discussions')
