from django.contrib import admin
from .models import Course
from .models import Enrollment

class EnrollmentInline(admin.TabularInline):
    model = Course.students.through
    extra = 1  # Number of extra empty rows to display

class CourseAdmin(admin.ModelAdmin):
    inlines = [EnrollmentInline]
    exclude = ('students',)  # Exclude the original students field

admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment)
