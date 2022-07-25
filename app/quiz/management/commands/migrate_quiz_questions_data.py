# import os
# import uuid
# import openpyxl
#
# from django.core.files import File
# from openpyxl_image_loader import SheetImageLoader
# from django.core.management.base import BaseCommand
# from spritacular.settings import BASE_DIR
# from quiz.models import Question, QuizOption
#
#
# class Command(BaseCommand):
#     help = 'This class is for populating the quiz questions data.'
#
#     def handle(self, *args, **options):
#         try:
#             print(os.path.join(BASE_DIR, 'labelled_imagery_updated.xlsx'))
#             wb = openpyxl.load_workbook(os.path.join(BASE_DIR, 'labelled_imagery_updated.xlsx'))
#             sheet = wb['Sheet1']
#             # calling the image_loader
#             image_loader = SheetImageLoader(sheet)
#             for i in range(2, 87):
#                 file_name = sheet.cell(i, 1).value
#                 # get the image (put the cell you need instead of 'A1')
#                 label = sheet.cell(i, 3).value
#                 # image = image_loader.get(sheet.cell(i, 2).coordinate)
#                 image = sheet.cell(i, 4).value
#                 drive_file_id = image.split('/')[-2]
#                 new_file_name = f"{uuid.uuid4()}.{file_name.split('.')[-1]}"
#                 # download_image(drive_file_id, new_file_name)
#
#                 image_open_file = open(f"{new_file_name}", 'rb')
#                 image_file_obj = File(image_open_file)  # creating django storage file object
#
#                 # is_user_credit=True for new watermarked images
#                 question_obj = Question.objects.create(is_user_credit=True, image=image_file_obj)
#                 os.remove(f"{new_file_name}")
#
#                 option_filter = QuizOption.objects.filter(title__in=label.strip().split(','))
#                 for opt in option_filter:
#                     question_obj.correct_option.add(opt)
#
#             self.stdout.write('Success!!')
#         except Exception as e:
#             self.stdout.write(f'Some error occurred while inserting quiz questions data. -- {e}')
#
