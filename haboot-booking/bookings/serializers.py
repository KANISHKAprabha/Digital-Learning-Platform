from rest_framework import serializers
from .models import *

class LSASearchSerializer(serializers.Serializer):
    skill=serializers.CharField(max_length=50)
    start_time=serializers.DateTimeField()
    end_time=serializers.DateTimeField()
    
    def validate(self,attrs):
        if attrs['start_time']>=attrs["end_time"]:
            raise serializers.ValidationError(
                "start_time must be before end time."
            )
        return attrs
    
    
    
class LSASearchResultSerializer(serializers.ModelSerializer):
    overlapping_bookings=serializers.IntegerField(read_only=True)
    class Meta:
        model=LSAProfile
        fields=[
            "id",
            "name",
            "skills",
            "qualification",
            "experience_years",
            "max_concurrent_students",
            "overlapping_bookings",
        ]
    