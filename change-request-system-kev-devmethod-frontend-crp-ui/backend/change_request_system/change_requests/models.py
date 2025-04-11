from django.db import models

class ChangeRequest(models.Model):
    project_name = models.CharField(max_length=255)
    change_number = models.CharField(max_length=50)
    requested_by = models.CharField(max_length=255)
    date_of_request = models.DateField()
    presented_to = models.CharField(max_length=255)
    change_name = models.CharField(max_length=255)
    description = models.TextField()
    reason = models.TextField()
    effect_on_deliverables = models.TextField()
    effect_on_organization = models.TextField()
    effect_on_schedule = models.TextField()
    effect_of_not_approving = models.TextField()

    def __str__(self):
        return f"{self.change_number} - {self.change_name}"

class CostItem(models.Model):
    change_request = models.ForeignKey(
        ChangeRequest,
        related_name='cost_items',
        on_delete=models.CASCADE
    )
    item_description = models.CharField(max_length=255)
    hours_reduction = models.IntegerField(default=0)
    hours_increase = models.IntegerField(default=0)
    dollars_reduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    dollars_increase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return self.item_description