import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .models import Table

def floor_plan_data(request):
    tables = Table.objects.filter(is_active=True).values(
        'id', 'name', 'min_covers', 'max_covers', 'section',
        'position_x', 'position_y', 'width', 'height', 'is_fixed'
    )
    return JsonResponse(list(tables), safe=False)

def floor_plan_editor(request):
    return render(request, 'tables/floor_plan_editor.html')

@require_POST
@csrf_protect
def update_table_position(request, table_id):
    data = json.loads(request.body)
    table = Table.objects.get(id=table_id, is_active=True)
    table.position_x = data['position_x']
    table.position_y = data['position_y']
    table.save(update_fields=['position_x', 'position_y'])
    return JsonResponse({'status': 'ok'})