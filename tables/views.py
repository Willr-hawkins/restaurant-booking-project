import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .models import Table, TableCombination
from .forms import TableForm, TableCombinationForm
from staff.decorators import manager_required
from bookings.models import Booking

TURNING_SOON_MINUTES = 20
STATUS_PRIORITY = {'free': 0, 'turning_soon': 1, 'seated': 2}

@manager_required
def floor_plan_data(request):
    tables = Table.objects.filter(is_active=True).values(
        'id', 'name', 'min_covers', 'max_covers', 'section',
        'position_x', 'position_y', 'width', 'height', 'is_fixed'
    )
    return JsonResponse(list(tables), safe=False)

@manager_required
def floor_plan_editor(request):
    return render(request, 'tables/floor_plan_editor.html')

@manager_required
@require_POST
@csrf_protect
def update_table_position(request, table_id):
    data = json.loads(request.body)
    table = Table.objects.get(id=table_id, is_active=True)
    table.position_x = data['position_x']
    table.position_y = data['position_y']
    table.save(update_fields=['position_x', 'position_y'])
    return JsonResponse({'status': 'ok'})

@manager_required
def table_list(request):
    tables = Table.objects.filter(is_active=True).order_by('name')
    return render(request, 'tables/table_list.html', {'tables': tables})

@manager_required
def table_create(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table added.')
            return redirect('table_list')
    else:
        form = TableForm()
    return render(request, 'tables/table_form.html', {'form': form, 'title': 'Add Table'})

@manager_required
def table_edit(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table Updated')
            return redirect('table_list')
    else:
        form = TableForm(instance=table)
    return render(request, 'tables/table_form.html', {'form': form, 'title': f'Edit {table.name}'})

@manager_required
def table_delete(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table_ct = ContentType.objects.get_for_model(Table)
    future_bookings = Booking.objects.filter(
        table_content_type=table_ct,
        table_object_id=table_id,
        date__gte=timezone.now().date(),
        status='confirmed',
    )

    if request.method == 'POST' and not future_bookings.exists():
        table.is_active = False
        table.save(update_fields=['is_active'])
        messages.success(request, f'{table.name} removed from the floor plan.')
        return redirect('table_list')
    
    other_tables = Table.objects.filter(is_active=True).exclude(id=table_id)
    return render(request, 'tables/table_confirm_delete.html', {
        'table': table,
        'future_bookings': future_bookings,
        'other_tables': other_tables,
    })

@manager_required
def reassign_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        new_table = get_object_or_404(Table, id=request.POST.get('new_table_id'), is_active=True)
        booking.assigned_table = new_table
        booking.save()
        messages.success(request, f'Booking reassigned to {new_table.name}.')
    return redirect('table_delete', table_id=request.POST.get('table_id'))

@manager_required
def combination_list(request):
    combinations = TableCombination.objects.filter(is_active=True)
    return render(request, 'tables/combination_list.html', {'combinations': combinations})
    
@manager_required
def combination_create(request):
    if request.method == 'POST':
        form = TableCombinationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Combination created.')
            return redirect('combination_list')
    else:
        form = TableCombinationForm()
    return render(request, 'tables/combination_form.html', {'form': form, 'title': 'Add Combination'})

@manager_required
def combination_edit(request, combination_id):
    combination = get_object_or_404(TableCombination, id=combination_id)
    if request.method == 'POST':
        form = TableCombinationForm(request.POST, instance=combination)
        if form.is_valid():
            form.save()
            messages.success(request, 'Combination updated.')
            return redirect('combination_list')
    else:
        form = TableCombinationForm(instance=combination)
    return render(request, 'tables/combination_form.html', {'form': form, 'title': f'Edit {combination}'})

@manager_required
def combination_delete(request, combination_id):
    combination = get_object_or_404(TableCombination, id=combination_id)
    if request.method == 'POST':
        combination.is_active = False
        combination.save(update_fields=['is_active'])
        messages.success(request, 'Combination removed.')
        return redirect('combination_list')
    return render(request, 'tables/combination_confirm_delete.html', {'combination': combination})
    
def compute_table_statuses():
    """
    Returns {table_id: status} for every active table, based on today's confirmed
    bookings. A combinationn booking marks ALL its member tables - since the floor
    plan only ever shows individual table boxes, not combination boxes.
    """
    now = timezone.localtime()
    today = now.date()
    now_dt = datetime.combine(today, now.time())

    statuses = {t.id: 'free' for t in Table.objects.filter(is_active=True)}

    table_ct = ContentType.objects.get_for_model(Table)
    combo_ct = ContentType.objects.get_for_model(TableCombination)
    todays_bookings = Booking.objects.filter(date=today, status='confirmed')

    for booking in todays_bookings:
        start = datetime.combine(today, booking.time)
        seated_until = start + timedelta(minutes=booking.predicted_duration_minutes)
        occupied_until = seated_until + timedelta(minutes=booking.buffer_minutes)

        if start <= now_dt < seated_until:
            new_status = 'turning_soon' if (seated_until - now_dt) <= timedelta(minutes=TURNING_SOON_MINUTES) else 'seated'
        elif seated_until <= now_dt < occupied_until:
            new_status = 'turning_soon'
        else:
            continue

        if booking.table_content_type_id == table_ct.id:
            table_ids = [booking.table_object_id]
        elif booking.table_content_type_id == combo_ct.id:
            combo = TableCombination.objects.filter(id=booking.table_object_id).first()
            table_ids = list(combo.tables.values_list('id', flat=True)) if combo else []
        else:
            table_ids = []

        for tid in table_ids:
            if tid in statuses and STATUS_PRIORITY[new_status] > STATUS_PRIORITY[statuses[tid]]:
                statuses[tid] = new_status
    
    return statuses

@manager_required
def floor_status_view(request):
    return render(request, 'tables/floor_status.html')

@manager_required
def floor_status_data(request):
    statuses = compute_table_statuses()
    tables = Table.objects.filter(is_active=True).values(
        'id', 'name', 'position_x', 'position_y', 'width', 'height', 'is_fixed'
    )
    data = []
    for t in tables:
        t['status'] = statuses.get(t['id'], 'free')
        data.append(t)
    return JsonResponse(data, safe=False)