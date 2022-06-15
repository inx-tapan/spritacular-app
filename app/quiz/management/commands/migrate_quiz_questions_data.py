import os
import sys
import uuid
from io import BytesIO

import openpyxl
from django.core.files.uploadedfile import InMemoryUploadedFile

from openpyxl_image_loader import SheetImageLoader
from django.core.management.base import BaseCommand
from spritacular.settings import BASE_DIR
from quiz.models import Question, QuizOption


class Command(BaseCommand):
    help = 'This class is for populating the quiz questions data.'

    def handle(self, *args, **options):
        try:
            print(os.path.join(BASE_DIR, 'quiz_data.xlsx'))
            wb = openpyxl.load_workbook(os.path.join(BASE_DIR, 'quiz_data.xlsx'))
            sheet = wb['Sheet1']
            # calling the image_loader
            image_loader = SheetImageLoader(sheet)
            for i in range(2, 84):
                file_name = sheet.cell(i, 1).value
                # get the image (put the cell you need instead of 'A1')
                image = image_loader.get(sheet.cell(i, 2).coordinate)
                label = sheet.cell(i, 3).value

                # print(f"{i}==>{QuizOption.objects.filter(title__in=label.strip().split(','))}==>{label.strip().split(',')}==>")
                # print("**********")

                output = BytesIO()
                ext = image.format
                image.save(output, format=ext, quality=70)
                output.seek(0)

                file_obj = InMemoryUploadedFile(
                            output,
                            'ImageField',
                            f"{uuid.uuid4()}.{file_name.split('.')[-1]}",
                            f"image/{file_name.split('.')[-1]}",
                            sys.getsizeof(output),
                            None,
                        )

                question_obj = Question.objects.create(image=file_obj)
                option_filter = QuizOption.objects.filter(title__in=label.strip().split(','))
                for opt in option_filter:
                    question_obj.correct_option.add(opt)

            self.stdout.write('Success!!')
        except Exception as e:
            self.stdout.write(f'Some error occurred while inserting quiz questions data. -- {e}')

