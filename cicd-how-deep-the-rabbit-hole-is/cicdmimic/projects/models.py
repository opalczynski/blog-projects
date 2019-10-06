from enum import Enum

from django.db import models


class BuildResultE(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3
    PENDING = 4


class Project(models.Model):
    name = models.CharField(max_length=256)
    local_path = models.CharField(max_length=2048)


class Build(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    result = models.PositiveSmallIntegerField(choices=[(choice.value, choice.name) for choice in BuildResultE],
                                              default=BuildResultE.PENDING.value)
    output = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def duration(self):
        # returns the build duration in seconds;
        if not self.finished_at or not self.started_at:
            return 'N/A'
        return (self.finished_at - self.started_at).total_seconds


class EnvironmentVariable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    value = models.CharField(max_length=512)
