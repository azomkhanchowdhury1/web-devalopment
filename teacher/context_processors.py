from .models import Teacher

def teacher_context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            context['current_teacher'] = request.user.teacher
        except Teacher.DoesNotExist:
            pass
    return context