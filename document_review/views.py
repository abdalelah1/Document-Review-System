from django.views.generic import TemplateView
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.generic import ListView
from .forms import *    
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import File,Custom_User,ReviewOperation
from django.views.generic import CreateView
from django.urls import reverse_lazy
from tinymce import models as tinymce_models
from django.views.generic import DetailView

class LoginView(TemplateView):
    template_name = 'login/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': CustomAuthenticationForm()})

    def post(self, request, *args, **kwargs):
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                print(user)
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request,'Invalid username or password')
        return render(request, self.template_name, {'form': form})
class AccessDeniedView(TemplateView):
    template_name = 'access_denied/access_denied.html'
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index/index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
class FileUploadView(LoginRequiredMixin, CreateView):
    model = File
    template_name = 'upload_file/upload_file.html'
    fields = ['file', 'file_type', 'description']
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        custom_user = Custom_User.objects.get(user=request.user)
        if custom_user.role not in [Custom_User.Role.ASSISTANT, Custom_User.Role.AUDITOR]:
            return redirect(reverse('access_denied'))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        file_type = request.POST.get('file_type')
        description = request.POST.get('description')
        uploaded_by = request.user

        # Save file to the database
        new_file = File(
            file=file,
            file_type=FileType.objects.all().first(),
            description=description,
            uploaded_by=uploaded_by
        )
        new_file.save()

        custom_user = Custom_User.objects.get(user=request.user)

        if custom_user.role == Custom_User.Role.ASSISTANT:
            # Find an auditor to review the file
            auditor = Custom_User.objects.filter(role=Custom_User.Role.AUDITOR).first()
            if auditor:
                ReviewOperation.objects.create(
                    file=new_file,
                    reviewed_by=auditor.user,
                    operation_type='pending'
                )
        elif custom_user.role == Custom_User.Role.AUDITOR:
            # Find a supervisor to review the file
            supervisor = Custom_User.objects.filter(role=Custom_User.Role.SUPERVISOR).first()
            if supervisor:
                ReviewOperation.objects.create(
                    file=new_file,
                    reviewed_by=supervisor.user,
                    operation_type='pending'
                )

        return super().post(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tinymce'] = tinymce_models.HTMLField()
        return context

class ReviewRequestsView(ListView):
    model = ReviewOperation
    template_name = 'requests/requests.html'
    context_object_name = 'review_requests'

    def get_queryset(self):
        return ReviewOperation.objects.filter(
            reviewed_by=self.request.user,
            file__is_reviewed=False
        )

class ReviewRequestDetailView(DetailView):

    model = ReviewOperation
    template_name = 'review_request_detail/review_request_detail.html'
    context_object_name = 'review_request'

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            self.object = super().get_object(queryset=queryset)
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_request = self.get_object()
        context['file'] = review_request.file
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        review_request = self.get_object()
        file = review_request.file
        error_message = None

        if 'confirm' in request.POST:
            new_file = request.FILES.get('file')
            if new_file and file.uploaded_by == request.user:
                    file.file = new_file
                    file.description = request.POST.get('description')
                    file.save()
                    review_request.operation_type = 'pending'
                    review_request.save()
                    return redirect('user_files')
            else:
                error_message = "You must re-upload the file."

        elif 'accept' in request.POST:
            review_request.operation_type = 'accept'
            review_request.comments = request.POST.get('comments')
            review_request.save()
            if request.user.custom_user.role=='AUDITOR':
                supervisor=Custom_User.objects.filter(role='SUPERVISOR').first()
                ReviewOperation.objects.create(
                    file=review_request.file,
                    forward_by=request.user,
                    reviewed_by=supervisor.user,
                    operation_type='pending'
              
                )
            if request.user.custom_user.role=='SUPERVISOR':
                supervisor=Custom_User.objects.filter(role='MANAGER').first()
                ReviewOperation.objects.create(
                    file=review_request.file,
                    forward_by=request.user,
                    reviewed_by=supervisor.user,
                    operation_type='pending'
              
                )
            
             
            return redirect('review_requests')
            
        elif 'reject' in request.POST:
            review_request.operation_type = 'reject'
            review_request.comments = request.POST.get('comments')
            review_request.save()
            return redirect('review_requests')
        elif 'request_modification' in request.POST:
            review_request.operation_type = 'request_modification'
            review_request.comments = request.POST.get('comments')
            review_request.save()
            return redirect('review_requests')
        elif 'accept-directly' in request.POST:
            print(review_request.file.is_reviewed)
            review_request.file.is_reviewed = True
            review_request.operation_type = 'accept'
            review_request.file.save()
            review_request.save()
            return redirect('review_requests')

        context = self.get_context_data()
        context['error_message'] = error_message
        return self.render_to_response(context)
    

class UserFilesView(LoginRequiredMixin, ListView):
    model = File
    template_name = 'user_files/user_files.html'
    context_object_name = 'files'
  

    def get_queryset(self):
        return File.objects.filter(uploaded_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        custom_user = Custom_User.objects.get(user=self.request.user)
        files_with_reviews = []

        for file in context['files']:
            if custom_user.role == Custom_User.Role.ASSISTANT:
                review = ReviewOperation.objects.filter(file=file, reviewed_by__custom_user__role=Custom_User.Role.AUDITOR).first()
            elif custom_user.role == Custom_User.Role.AUDITOR:
                review = ReviewOperation.objects.filter(file=file, reviewed_by__custom_user__role=Custom_User.Role.SUPERVISOR).first()
            else:
                review = None
            files_with_reviews.append({
                'file': file,
                'review': review
            })
        forwarded_reviews = ReviewOperation.objects.filter(forward_by=self.request.user)

        context['files_with_reviews'] = files_with_reviews
        context['forwarded_reviews'] = forwarded_reviews
        return context
class AllFilesView(LoginRequiredMixin, ListView):
    model = File
    template_name = 'all_files/all_files.html'
    context_object_name = 'files'
    def dispatch(self, request, *args, **kwargs):   
        custom_user = Custom_User.objects.get(user=request.user)
        if not  custom_user.role == Custom_User.Role.MANAGER:
            return redirect(reverse('access_denied'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files_with_reviews = []

        for file in File.objects.filter(is_reviewed=True):
            reviews = ReviewOperation.objects.filter(file=file)
            reviewers = set(review.reviewed_by for review in reviews)
            files_with_reviews.append({
                'file': file,
                'reviewers': reviewers
            })

        context['files_with_reviews'] = files_with_reviews
        return context
class SupervisorRequestsView(LoginRequiredMixin, ListView):
    model = ReviewOperation
    template_name = 'supervisor_requests/supervisor_requests.html'
    context_object_name = 'review_operations'

    def get_queryset(self):
        # عرض الطلبات التي ليست مقبولة
        return ReviewOperation.objects.filter(
            reviewed_by__custom_user__role=Custom_User.Role.SUPERVISOR
        ).exclude(operation_type='accept')  # استبعاد الطلبات المقبولة

    def dispatch(self, request, *args, **kwargs):
        custom_user = Custom_User.objects.get(user=request.user)
        if custom_user.role != Custom_User.Role.MANAGER:
            return redirect(reverse('access_denied'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        files_with_reviews = {}
        for review_op in context['review_operations']:
            file = review_op.file
            if file not in files_with_reviews:
                files_with_reviews[file] = {
                    'file': file,
                    'operations': [],
                    'reviewers': set(),
                    'current_status': review_op.operation_type,
                    'operation_date': review_op.operation_date,
                    'comments': review_op.comments  # إضافة التعليقات
                }
            files_with_reviews[file]['operations'].append(review_op)
            files_with_reviews[file]['reviewers'].update(
                op.reviewed_by for op in file.review_operations.all()
            )
            # تحديث الحالة الحالية إذا كانت العملية أكثر حداثة
            if review_op.operation_date > files_with_reviews[file]['operation_date']:
                files_with_reviews[file]['current_status'] = review_op.operation_type
                files_with_reviews[file]['operation_date'] = review_op.operation_date
                files_with_reviews[file]['comments'] = review_op.comments  # تحديث التعليقات

        context['files_with_reviews'] = files_with_reviews.values()
        return context

class FileRequestListView(ListView):
    model = FileRequest
    template_name = 'file_requests/file_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        requests = super().get_queryset()
        for request in requests:
            request.response = FileResponse.objects.filter(file_request=request).first()
        return requests
    
class FileRequestCreateView(LoginRequiredMixin, CreateView):
    model = FileRequest
    form_class = FileRequestForm
    template_name = 'file_request_form/file_request_form.html'
    success_url = reverse_lazy('file_requests')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetching only auditors
        context['auditors'] = Custom_User.objects.filter(role=Custom_User.Role.AUDITOR)
        return context

    def form_valid(self, form):
        
        form.instance.requested_by = self.request.user.custom_user
        return super().form_valid(form)
class UserFileRequestListView(LoginRequiredMixin, ListView):
    model = FileRequest
    template_name = 'file_requests/manage_requests.html'
    context_object_name = 'requests'
    def dispatch(self, request, *args, **kwargs):
        custom_user = Custom_User.objects.get(user=request.user)
        if custom_user.role != Custom_User.Role.AUDITOR:
            return redirect(reverse('access_denied'))
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self):
        # Filter requests to show only those created by the current user
        return FileRequest.objects.filter(requested_from=self.request.user.custom_user)
class FileRequestDetailView(LoginRequiredMixin, DetailView):
    model = FileRequest
    template_name = 'file_requests/file_requests_details.html'
    context_object_name = 'review_request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.custom_user.role
        context['is_auditor'] = user_role == 'AUDITOR'
        context['file_response'] = FileResponse.objects.filter(file_request=self.object).first()
        if user_role == 'AUDITOR' and not context['file_response']:
            context['response_form'] = FileResponseForm()
        return context  
    def dispatch(self, request, *args, **kwargs):
        custom_user = Custom_User.objects.get(user=request.user)
        if custom_user.role not in [Custom_User.Role.SUPERVISOR, Custom_User.Role.AUDITOR ,Custom_User.Role.MANAGER ]:
            return redirect(reverse('access_denied'))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = FileResponseForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.file_request = self.object.id
            form.save()
            return redirect('manage_requests')
        context = self.get_context_data()
        context['response_form'] = form
        return self.render_to_response(context)