import json
import re
from rest_framework import serializers
from gate_core.models import UnitChoice
from daily_needs_gatein.models import DailyNeedGateEntry, DailyNeedGateEntryItem


class DailyNeedGateEntryItemSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=UnitChoice.objects.all())

    class Meta:
        model = DailyNeedGateEntryItem
        fields = ("id", "line_no", "material_name", "quantity", "unit")
        read_only_fields = ("id",)

    def validate_material_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Material name must be at least 2 characters")
        return value.strip() if value else value

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.unit:
            data["unit"] = {
                "id": instance.unit.id,
                "name": instance.unit.name,
            }
        return data


class DailyNeedGateEntrySerializer(serializers.ModelSerializer):
    items = DailyNeedGateEntryItemSerializer(many=True, required=False)

    class Meta:
        model = DailyNeedGateEntry
        exclude = ("created_by", "vehicle_entry")
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "material_name": {"required": False},
            "quantity": {"required": False},
            "unit": {"required": False},
        }

    def to_internal_value(self, data):
        if hasattr(data, "dict"):
            mutable_data = data.dict()
        else:
            mutable_data = dict(data)

        raw_items = mutable_data.get("items")
        if isinstance(raw_items, str):
            try:
                mutable_data["items"] = json.loads(raw_items)
            except json.JSONDecodeError:
                raise serializers.ValidationError({"items": "Invalid items JSON"})

        return super().to_internal_value(mutable_data)

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number")
        return value

    def validate_contact_number(self, value):
        if value:
            cleaned = re.sub(r'[\s\-]', '', value)
            if not re.match(r'^\+?[0-9]{10,15}$', cleaned):
                raise serializers.ValidationError(
                    "Invalid phone number format. Use 10-15 digits, optionally starting with +"
                )
        return value

    def validate_supplier_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Supplier name must be at least 2 characters")
        return value.strip() if value else value

    def validate_material_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Material name must be at least 2 characters")
        return value.strip() if value else value

    def validate(self, attrs):
        items = attrs.get("items") or []
        if not items:
            missing_fields = []
            for field in ("material_name", "quantity", "unit"):
                if not attrs.get(field):
                    missing_fields.append(field)
            if missing_fields:
                raise serializers.ValidationError({
                    "items": "Please enter at least one material item",
                })

        if items:
            first_item = items[0]
            attrs["material_name"] = first_item["material_name"]
            attrs["quantity"] = first_item["quantity"]
            attrs["unit"] = first_item["unit"]

        return attrs

    def _replace_items(self, instance, items_data):
        if not items_data:
            items_data = [{
                "line_no": 1,
                "material_name": instance.material_name,
                "quantity": instance.quantity,
                "unit": instance.unit,
            }]

        instance.items.all().delete()
        for index, item_data in enumerate(items_data, start=1):
            DailyNeedGateEntryItem.objects.create(
                daily_need_entry=instance,
                line_no=index,
                material_name=item_data["material_name"],
                quantity=item_data["quantity"],
                unit=item_data["unit"],
            )

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        instance = super().create(validated_data)
        self._replace_items(instance, items_data)
        return instance

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        instance = super().update(instance, validated_data)
        if items_data is not None:
            self._replace_items(instance, items_data)
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.item_category:
            data['item_category'] = {
                'id': instance.item_category.id,
                'category_name': instance.item_category.category_name
            }
        if instance.receiving_department:
            data["receiving_department"] = {
                'id': instance.receiving_department.id,
                'name': instance.receiving_department.name
            }
        if instance.unit:
            data['unit'] = {
                'id': instance.unit.id,
                'name': instance.unit.name
            }

        items = list(instance.items.all())
        if items:
            data["items"] = DailyNeedGateEntryItemSerializer(items, many=True).data
        else:
            data["items"] = [{
                "id": None,
                "line_no": 1,
                "material_name": instance.material_name,
                "quantity": str(instance.quantity),
                "unit": data.get("unit"),
            }]
        return data



class CategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyNeedGateEntry.item_category.field.related_model
        fields = "__all__"
