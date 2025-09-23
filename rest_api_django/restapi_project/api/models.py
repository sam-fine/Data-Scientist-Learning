from django.db import models

class Task(models.Model):
    """
    Task model for managing to-do style tasks.

    Fields:
        title (CharField): A short name or title of the task.
        description (TextField): A longer text giving details about the task.
        completed (BooleanField): Marks whether the task is done (True) or not (False).

    Methods:
        __str__: Returns the task's title when the object is printed or displayed.
    """
    # Short text field for the task's title (e.g., "Buy groceries")
    title = models.CharField(max_length=255)

    # Larger text field for details about the task (e.g., "Buy milk, bread, and eggs")
    description = models.TextField()

    # Boolean value that indicates if the task is completed or not
    completed = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the title of the task as its string representation.
        Helpful when viewing objects in the Django admin or shell.
        """
        return self.title