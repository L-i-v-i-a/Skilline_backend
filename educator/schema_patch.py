# educator/schema_patch.py
from drf_spectacular.openapi import AutoSchema


class SafeUserAutoSchema(AutoSchema):
    """
    Prevents drf-spectacular from crashing on custom related_name
    for groups/user_permissions in custom User model
    """
    def _map_model_field(self, field, direction):
        # Skip fields that cause NoneType._meta crash
        if field.model_field and field.model_field.name in ('groups', 'user_permissions'):
            return None  # Skip completely - no schema entry for these
        return super()._map_model_field(field, direction)