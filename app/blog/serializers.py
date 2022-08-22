from rest_framework.serializers import ModelSerializer
from .models import MeetTheTeam


class MeetTheTeamSerializer(ModelSerializer):

    class Meta:
        model = MeetTheTeam
        fields = '__all__'
