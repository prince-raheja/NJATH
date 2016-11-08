from django.core.management.base import BaseCommand, CommandError
from game.models import Questions


class Command(BaseCommand):
	help = 'Saves sample questions for njath'

	def handle(self, *args, **kwargs):
		questions_count = Questions.objects.all().count()
		if questions_count > 0:
			answer = raw_input('Questions Table is not Empty.\nAre you sure you want to continue (y/n)')
			# answer = 'y'
			if answer == 'y':
				self.save_questions()
			else:
				self.stdout.write(self.style.SUCCESS('Aborting.......'))
		else:
			self.save_questions()

	def save_questions(self):
		Questions.objects.all().delete()
		questions = range(1,9)
		levels = range(1,7)
		questions_list = []
		for i in levels:
			for j in questions:
				questions_list.append(Questions(level=i, question='Question '+str(j), answer='answer'+str(j),\
					slug='level-'+str(i)+'-question-'+str(j), penalty=8*i, score=10*i,))

		Questions.objects.bulk_create(questions_list)
		self.stdout.write(self.style.SUCCESS('Done'))