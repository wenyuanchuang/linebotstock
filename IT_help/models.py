from django.db import models

# Create your models here.
class Todo(models.Model):  
    todo = models.TextField()

    def __str__(self):  
        return self.todo[:50]
