from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer

@api_view(['GET', 'POST']) #decorator (adds extra logic to function) that allows this function to handle only the specified HTTP methods.
def task_list(request):
    """
    Handle requests for the list of tasks.

    GET:
        - Retrieve all Task objects from the database.
        - Serialize them into JSON and return in the response.

    POST:
        - Accept JSON data to create a new Task.
        - Validate the data using TaskSerializer.
        - Save to the database if valid, else return errors.
    """
    if request.method == 'GET':
        # Get all tasks from the database
        tasks = Task.objects.all()

        # Serialize multiple objects with many=True
        serializer = TaskSerializer(tasks, many=True)

        # Return serialized data as JSON
        return Response(serializer.data)

    elif request.method == 'POST':
        # Deserialize incoming JSON data
        serializer = TaskSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            # Save the new Task to the database
            serializer.save()
            # Return created task with 201 status code
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors with 400 status code
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    """
    Handle requests for a single task by its primary key (id).

    GET:
        - Retrieve a single Task and return it as JSON.

    PUT:
        - Update a Task with incoming JSON data.
        - Validate and save changes if valid.

    DELETE:
        - Remove the Task from the database.
    """
    try:
        # Try to get the task by primary key
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        # Return 404 if the task does not exist
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Serialize the task object
        serializer = TaskSerializer(task)
        # Return serialized data as JSON
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Deserialize incoming data and update the existing task
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            # Save updates to the database
            serializer.save()
            return Response(serializer.data)
        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the task from the database
        task.delete()
        # Return 204 No Content to indicate successful deletion
        return Response(status=status.HTTP_204_NO_CONTENT)

