from django.db import models

class ToDoItem(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

class UserInput(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text