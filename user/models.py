from django.db import models

class User(models.Model):
    userId = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', unique=True, max_length=64)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=32)  # Field name made lowercase.
    permGroup = models.CharField(db_column='PermGroup', max_length=13)  # Field name made lowercase.
    regDate = models.DateTimeField(db_column='RegDate')  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=256)  # Field name made lowercase.
    nickname = models.CharField(db_column='Nickname', max_length=32)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'
