from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    Purpose:
        - Converts Task model instances into JSON (for API responses).
        - Converts JSON input into Task model instances (for saving to the database).

    Meta:
        model (Task): The model this serializer is based on.
        fields ('__all__'): Includes all fields of the Task model 
                            (title, description, completed).
    """

    class Meta:
        # Connect this serializer to the Task model
        model = Task

        # Include all fields from the Task model in the serializer
        # (title, description, completed will be automatically included)
        fields = '__all__'
