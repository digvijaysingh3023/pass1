from django.db import models

# Create your models here.
class Pass(models.Model):
    pass_icon=models.ImageField(upload_to="image_uploads/passicon/")

    def __str__(self):
        return str(self.pass_icon.name)