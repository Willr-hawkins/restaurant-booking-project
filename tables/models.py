from django.db import models

class Table(models.Model):
    SECTION_CHOICES = [
        ('main', 'Main Dining'),
        ('window', 'Window'),
        ('patio', 'Patio'),
        ('bar', 'Bar'),
        ('private', 'Private Room'),
    ]

    name = models.CharField(max_length=50)  # e.g. "Table 4", "Window 2"
    min_covers = models.PositiveIntegerField(default=1)
    max_covers = models.PositiveIntegerField()
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='main')

    # Floor plan position (used by the drag-and-drop editor in Sprint 2)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)

    is_active = models.BooleanField(
        default=True,
        help_text="Inactive tables are soft-deleted — hidden from the floor plan but kept for historical bookings."
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.min_covers}-{self.max_covers} covers)"
    
class TableCombination(models.Model):
    """ A set of tables that can be pushed together to seat a larger party. """
    name = models.CharField(max_length=100, blank=True) # Optional, e.g. "Tables 4+5"
    tables = models.ManyToManyField(Table, related_name="combinations")
    min_covers = models.PositiveIntegerField()
    max_covers = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.name:
            return self.name
        return f"Combination ({self.min_covers}-{self.max_covers} covers)"
