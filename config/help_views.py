"""
Views for help and documentation
"""
from django.shortcuts import render


def documentation(request):
    """
    Display help documentation page
    """
    return render(request, 'help/documentation.html')
