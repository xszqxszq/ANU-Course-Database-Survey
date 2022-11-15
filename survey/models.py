from django.db import models
from user.models import User

class RecordAnswer(models.Model):
    record = models.OneToOneField('RecordInfo', models.DO_NOTHING, db_column='RecordID', primary_key=True)
    question = models.ForeignKey('SurveyQuestion', models.DO_NOTHING, db_column='QuestionID')
    multiID = models.IntegerField(db_column='MultiID', default=0)
    option = models.ForeignKey('SurveyOption', models.DO_NOTHING, db_column='OptionID', blank=True, null=True)
    answer = models.CharField(db_column='Answer', max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'RecordAnswer'
        unique_together = (('record', 'question'),)


class RecordInfo(models.Model):
    id = models.AutoField(db_column='RecordID', primary_key=True)
    survey = models.ForeignKey('SurveyInfo', models.DO_NOTHING, db_column='SurveyID')
    respondent = models.ForeignKey('Respondent', models.DO_NOTHING, db_column='RespondentID')
    submitDate = models.DateTimeField(db_column='SubmitDate', auto_now=True)

    class Meta:
        managed = False
        db_table = 'RecordInfo'


class Respondent(models.Model):
    id = models.AutoField(db_column='RespondentID', primary_key=True)
    firstName = models.CharField(db_column='FirstName', max_length=64)
    lastName = models.CharField(db_column='LastName', max_length=64)
    email = models.CharField(db_column='Email', max_length=320)
    group = models.ForeignKey('RespondentGroup', models.DO_NOTHING, db_column='GroupID', blank=True, null=True)
    company = models.CharField(db_column='Company', max_length=64, blank=True, null=True)
    position = models.CharField(db_column='Position', max_length=32, blank=True, null=True)
    phone = models.CharField(db_column='Phone', max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Respondent'


class RespondentGroup(models.Model):
    id = models.AutoField(db_column='GroupID', primary_key=True)
    name = models.CharField(db_column='Name', max_length=16)
    company = models.CharField(db_column='Company', max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'RespondentGroup'


class SurveyInfo(models.Model):
    id = models.AutoField(db_column='SurveyID', primary_key=True)
    creator = models.ForeignKey(User, models.DO_NOTHING, db_column='CreatorID')
    title = models.CharField(db_column='Title', max_length=128)
    startDate = models.DateTimeField(db_column='StartDate')
    endDate = models.DateTimeField(db_column='EndDate')
    createDate = models.DateTimeField(db_column='CreateDate')
    reminders = models.IntegerField(db_column='Reminders')
    status = models.CharField(db_column='Status', max_length=8)

    class Meta:
        managed = False
        db_table = 'SurveyInfo'


class SurveyQuestion(models.Model):
    id = models.AutoField(db_column='QuestionID', primary_key=True)
    survey = models.ForeignKey(SurveyInfo, models.DO_NOTHING, db_column='SurveyID')
    questionType = models.CharField(db_column='QuestionType', max_length=8)
    content = models.CharField(db_column='Content', max_length=512)

    class Meta:
        managed = False
        db_table = 'SurveyQuestion'


class SurveyOption(models.Model):
    id = models.AutoField(db_column='OptionID', primary_key=True)
    question = models.ForeignKey(SurveyQuestion, models.DO_NOTHING, db_column='QuestionID')
    value = models.CharField(db_column='Value', max_length=128)

    class Meta:
        managed = False
        db_table = 'SurveyOption'