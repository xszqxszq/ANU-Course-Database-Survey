from django.shortcuts import render, redirect
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from survey.models import *
from user.utils import *

import json
import datetime
import pytz
import csv
from io import StringIO

def view(request):
	context = {}
	surveyID = request.GET.get('id')
	survey = SurveyInfo.objects.filter(id=surveyID).first()
	if not survey or survey.status != 'Normal':
		return redirect('/')
	context['title'] = survey.title
	context['surveyID'] = survey.id
	context['questions'] = enumerate(SurveyQuestion.objects.filter(survey=surveyID).prefetch_related('surveyoption_set').all()) 
	return render(request, 'survey.html', context=context)

def submit(request):
	surveyID = request.POST.get('survey_id')
	if not surveyID:
		return redirect('/')
	survey = SurveyInfo.objects.filter(id=surveyID).first()
	if not survey:
		return redirect('/')
	questions = SurveyQuestion.objects.filter(survey=surveyID).prefetch_related('surveyoption_set').all()
	respondent = Respondent.objects.filter(email=request.POST.get('email')).first()
	if not respondent:
		respondent = Respondent.objects.create(email=request.POST.get('email'))
	record = RecordInfo.objects.create(survey=survey, respondent=respondent)
	for q in questions:
		if str(q.id) not in request.POST:
			continue
		if q.questionType in ['Text', 'LongText']:
			answer = request.POST.get(str(q.id))
			RecordAnswer.objects.create(record=record, question=q, answer=answer)
		elif q.questionType in ['Dropdown', 'Rating']:
			optionID = request.POST.get(str(q.id))
			option = SurveyOption.objects.filter(id=optionID).first()
			if option:
				RecordAnswer.objects.create(record=record, question=q, option=option)
		elif q.questionType == 'Checkbox':
			options = request.POST.getlist(str(q.id))
			for i, optionID in enumerate(options):
				option = SurveyOption.objects.filter(id=optionID).first()
				if option:
					RecordAnswer.objects.create(record=record, question=q, multiID=i, option=option)

	return redirect('/')

def create(request):
	user = getUser(request)
	context = {'title': 'Create survey'}
	if user:
		context['nickname'] = user.nickname
	else:
		return redirect('/user/login')
	if user.permGroup == 'DataAnalyst':
		return redirect('/survey/manage')
	if request.method == 'POST':
		r = json.loads(request.POST.get('content'))
		title = r['title']
		questions = r['questions']
		status = r['status']
		startDate = r['startdate']
		endDate = r['enddate']
		reminders = r['reminders']
		survey = SurveyInfo.objects.create(creator=user, title=title, startDate=startDate, endDate=endDate, createDate=datetime.datetime.now(), reminders=reminders, status=status)
		for qInfo in questions:
			question = SurveyQuestion.objects.create(survey=survey, questionType=qInfo['type'], content=qInfo['content'])
			for option in qInfo['options']:
				SurveyOption.objects.create(question=question, value=option)
		return JsonResponse({'status': 'ok'}, safe=False)
	else:
		return render(request, 'create.html', context=context)

# Due to tight schedule, we cannot implement splitting into pages
def manage(request):
	user = getUser(request)
	context = {'title': 'Manage survey'}
	if user:
		context['nickname'] = user.nickname
	else:
		return redirect('/user/login')
	surveyID = request.GET.get('id')
	if surveyID:
		context['survey'] = SurveyInfo.objects.filter(id=surveyID).first()
		if user.permGroup == 'SurveyCreator' and context['survey'].creator.userId != user.userId:
			return redirect('/survey/manage')
		context['records'] = RecordInfo.objects.filter(survey=context['survey']).count()
		context['user'] = user
		return render(request, 'details.html', context=context)
	else:
		if user.permGroup == 'SystemAdmin' or user.permGroup == 'DataAnalyst':
			context['surveyAll'] = SurveyInfo.objects.all()
		elif user.permGroup == 'SurveyCreator':
			context['surveyAll'] = SurveyInfo.objects.filter(creator=user).all()
		context['nowDate'] = datetime.datetime.now()
		return render(request, 'manage.html', context=context)

def delete(request):
	user = getUser(request)
	context = {}
	if user:
		context['nickname'] = user.nickname
	else:
		return redirect('/user/login')
	surveyID = request.GET.get('id')
	if surveyID:
		survey = SurveyInfo.objects.filter(id=surveyID).first()
		if not survey:
			return redirect('/survey/manage')
		questions = SurveyQuestion.objects.filter(survey=survey).prefetch_related('surveyoption_set').prefetch_related('recordanswer_set').all()
		records = RecordInfo.objects.filter(survey=survey).all()
		for i in questions:
			i.recordanswer_set.all().delete()
		for i in records:
			i.delete()
		for i in questions:
			i.surveyoption_set.all().delete()
			i.delete()
		survey.delete()
	return redirect('/survey/manage')

def end(request):
	user = getUser(request)
	context = {}
	if user:
		context['nickname'] = user.nickname
	else:
		return redirect('/user/login')
	surveyID = request.GET.get('id')
	if surveyID:
		survey = SurveyInfo.objects.filter(id=surveyID)
		if not survey.first():
			return redirect('/survey/manage')
		survey.update(endDate=datetime.datetime.now())
	return redirect('/survey/manage')

def records(request):
	user = getUser(request)
	context = {'title': 'Manage records'}
	if user:
		context['nickname'] = user.nickname
		context['user'] = user
	else:
		return redirect('/user/login')
	surveyID = request.GET.get('survey')
	recordID = request.GET.get('record')
	if surveyID:
		context['recordAll'] = RecordInfo.objects.filter(survey=surveyID).all()
		return render(request, 'records.html', context=context)
	elif recordID:
		context['record'] = RecordInfo.objects.filter(id=recordID).first()
		context['survey'] = SurveyInfo.objects.filter(id=context['record'].survey.id).first()
		if not context['survey']:
			return redirect('/survey/manage')
		context['questions'] = enumerate(SurveyQuestion.objects.filter(survey=context['survey']).prefetch_related('recordanswer_set').prefetch_related('surveyoption_set').all())
		context['options'] = [j.option.id for i in SurveyQuestion.objects.filter(survey=context['survey']).prefetch_related('recordanswer_set').all() for j in i.recordanswer_set.all() if j.option != None and j.record.id == int(recordID)]
		return render(request, 'record_details.html', context=context)
	else:
		return redirect('/survey/manage')

def analysis(request):
	user = getUser(request)
	context = {'title': 'Data analysis'}
	if user:
		context['nickname'] = user.nickname
		context['user'] = user
	else:
		return redirect('/user/login')
	surveyID = request.GET.get('id')
	if not surveyID:
		return redirect('/survey/manage')
	context['survey'] = SurveyInfo.objects.filter(id=surveyID).first()
	if not context['survey']:
		return redirect('/survey/manage')
	raw = SurveyQuestion.objects.filter(survey=context['survey']).prefetch_related('recordanswer_set').prefetch_related('surveyoption_set').all()
	questions = []
	for i in raw:
		q = {'id': i.id, 'content': i.content, 'questionType': i.questionType, 'info': i, 'options': {}, 'totalCount': 0, 'sum': 0, 'average': 0}
		for j in i.surveyoption_set.all():
			q['options'][j.id] = {'id': j.id, 'value': j.value, 'count': 0}
		for j in i.recordanswer_set.all():
			if not j.option or j.option.id not in q['options']:
				continue
			q['options'][j.option.id]['count'] += 1
			q['totalCount'] += 1
			if q['questionType'] == 'Rating':
				q['sum'] += int(j.option.value)
		for j in q['options'].values():
			if q['totalCount']:
				j['percentage'] = '%.1f' % (j['count'] / q['totalCount'] * 100)
			else:
				j['percentage'] = '0.0'
			if q['sum']:
				q['average'] = '%.1f' % (q['sum'] / q['totalCount'])
		questions.append(q)
	context['questions'] = enumerate(questions)
	return render(request, 'analysis.html', context=context)

def respondent(request):
	user = getUser(request)
	context = {'title': 'Manage respondent'}
	if user:
		context['nickname'] = user.nickname
		context['user'] = user
	else:
		return redirect('/user/login')
	if request.method == 'POST':
		if request.FILES:
			for f in request.FILES.getlist('file'):
				reader = csv.reader(StringIO(f.read().decode('UTF-8')))
				for row in reader:
					Respondent.objects.create(firstName=row[0], lastName=row[1], email=row[2], company=row[3], position=row[4], phone=row[5])
		else:
			groupTarget = [int(i) for i in request.POST.getlist('target')]
			groupName = request.POST.get('group-name')
			query = RespondentGroup.objects.filter(name=groupName)
			if query.count():
				group = query.first()
			else:
				group = RespondentGroup.objects.create(name=groupName)
			Respondent.objects.filter(id__in=groupTarget).update(group=group)
	respondents = Respondent.objects.all()
	context['count'] = {}
	for i in respondents:
		context['count'][i.id] = 0
	for i in RecordInfo.objects.values('respondent').annotate(count=Count('id')).filter(respondent__in=respondents).all():
		context['count'][i['respondent']] = i['count']
	context['respondentAll'] = [(i.id, i) for i in respondents]
	return render(request, 'respondent.html', context=context)