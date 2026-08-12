from django.http import JsonResponse
from .models import Table

def floor_plan_data(request):
    tables = Table.objects.filter(is_active=True).values(
        'id', 'name', 'min_covers', 'max_covers', 'section',
        'position_x', 'position_y', 'width', 'height',
    )
    return JsonResponse(list(tables), safe=False)
