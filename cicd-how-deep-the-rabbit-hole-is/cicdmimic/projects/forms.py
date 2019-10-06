from django.forms import ModelForm

from projects.models import Project, Build, EnvironmentVariable


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ("name", "local_path")


class BuildForm(ModelForm):
    class Meta:
        model = Build
        fields = ('project', )


class EnvironmentVariableForm(ModelForm):
    class Meta:
        model = EnvironmentVariable
        fields = ('project', 'name', 'value')
