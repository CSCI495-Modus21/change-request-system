from rest_framework import serializers
from .models import ChangeRequest, CostItem

class CostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostItem
        fields = [
            'id',
            'item_description',
            'hours_reduction',
            'hours_increase',
            'dollars_reduction',
            'dollars_increase'
        ]

class ChangeRequestSerializer(serializers.ModelSerializer):
    cost_items = CostItemSerializer(many=True)

    class Meta:
        model = ChangeRequest
        fields = [
            'id',
            'project_name',
            'change_number',
            'requested_by',
            'date_of_request',
            'presented_to',
            'change_name',
            'description',
            'reason',
            'effect_on_deliverables',
            'effect_on_organization',
            'effect_on_schedule',
            'effect_of_not_approving',
            'cost_items'
        ]

    def create(self, validated_data):
        cost_items_data = validated_data.pop('cost_items')
        change_request = ChangeRequest.objects.create(**validated_data)
        for cost_item_data in cost_items_data:
            CostItem.objects.create(
                change_request=change_request,
                **cost_item_data
            )
        return change_request