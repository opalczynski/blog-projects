import json

from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, DetailView

from projects.ci_runner import CIRunner
from projects.forms import ProjectForm, BuildForm, EnvironmentVariableForm
from projects.models import Project, Build, EnvironmentVariable


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['add_project_form'] = ProjectForm()
        return context


class ProjectAddView(CreateView):
    template_name = "index.html"
    model = Project
    queryset = Project.objects.all()
    form_class = ProjectForm

    def get_success_url(self):
        return reverse("index")


class ProjectDetailView(DetailView):
    model = Project
    pk_url_kwarg = "project_id"
    template_name = "project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['builds'] = Build.objects.filter(project=self.object).order_by('-id').all()
        context['variables'] = EnvironmentVariable.objects.filter(project=self.object).all()
        return context


class BuildDetailView(DetailView):
    model = Build
    pk_url_kwarg = "build_id"
    template_name = "build_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object'].output:
            context['build_details'] = json.loads(context['object'].output)
        return context


class BuildRunView(CreateView):
    template_name = "project_detail.html"
    model = Build
    queryset = Build.objects.all()
    form_class = BuildForm

    def form_valid(self, form):
        self.object = form.save()
        # before we return here - lets run the build actuall;
        ci_runner = CIRunner(project=self.object.project, build=self.object)
        ci_runner.run_ci()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project-detail", args=(self.object.project_id,))


class EnvironmentVariableCreateView(CreateView):
    template_name = "project_detail.html"
    model = EnvironmentVariable
    queryset = EnvironmentVariable.objects.all()
    form_class = EnvironmentVariableForm

    def get_success_url(self):
        return reverse("project-detail", args=(self.object.project_id,))
