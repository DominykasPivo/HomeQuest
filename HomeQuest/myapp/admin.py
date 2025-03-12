from django.contrib import admin
from .models import ToDoItem, UserInput

# Register your models here.
admin.site.register(ToDoItem)
admin.site.register(UserInput)
