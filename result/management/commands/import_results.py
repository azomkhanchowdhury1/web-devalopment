from django.core.management.base import BaseCommand
import csv
from result.models import Result, Student, Class, Subject
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Import results from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    
    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    student = Student.objects.get(roll_number=row['roll_number'])
                    subject = Subject.objects.get(code=row['subject_code'])
                    student_class = Class.objects.get(name=row['class_name'])
                    
                    Result.objects.create(
                        student=student,
                        student_class=student_class,
                        subject=subject,
                        exam_type=row['exam_type'],
                        marks_obtained=float(row['marks_obtained']),
                        total_marks=float(row['total_marks']),
                        created_by=User.objects.first()  # Or get appropriate user
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully imported result for {student.name}')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importing result: {str(e)}')
                    )