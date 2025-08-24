from django.db import models
from django.contrib.auth.models import User




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)
    github = models.URLField()
    linedin = models.URLField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader')
    members = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team')
    created_at = models.DateTimeField(auto_now_add=True)
    #track
    #submittion
    #Hackathon
    
    def __str__(self):
        return f"{self.name} Project - {self.leader.first_name} Leader"

class HackathonStatusChoices(models.TextChoices):
        OPENED = 'OPENED', 'Opened'
        CLOSED = 'CLOSED', 'Closed'
        ONGOING = 'ONGOING', 'OnGoing'
        FINISHED = 'FINISHED', 'Finished'

class Hackathon(models.Model):
    title = models.CharField(max_length=100)
    location = models.URLField()
    location = models.TextField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(auto_now_add=True)
    max_team_size = models.IntegerField()
    min_team_size = models.IntegerField()
    status = models.CharField(choices=HackathonStatusChoices.choices,max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} Hackathon"


class HackathonStage(models.Model):
      title = models.CharField(max_length=100)
      description = models.TextField()
      start_date = models.DateField(auto_now_add=True)
      end_date = models.DateField(auto_now_add=True)
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_stage")

      def __str__(self):
        return f"{self.title} Stage"


class HackathonTrack(models.Model):
      name = models.CharField(max_length=100)
      name = models.CharField(max_length=100)
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_track")

      def __str__(self):
        return f"{self.name} Track"

class HackathonRequirement(models.Model):
      description = models.TextField()
      hackathon = models.ForeignKey(Hackathon,on_delete=models.CASCADE, related_name="hackathon_requirement")

      def __str__(self):
        return f"{self.description} Requirement"
