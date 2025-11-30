def result_context(request):
    """
    Add result-related context to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'student'):
                context['student_profile'] = request.user.student
        except Student.DoesNotExist:
            pass
    
    return context