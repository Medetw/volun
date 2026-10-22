from typing import Dict, Any
from rest_framework import serializers
from apps.projects.models import Project, Category, Region, ProjectFormat, ProjectStatus
from apps.users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for Region model."""
    
    class Meta:
        model = Region
        fields = ['id', 'name', 'code', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for project list (short version)."""
    category = CategorySerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    organization_name = serializers.SerializerMethodField()
    volunteers_count = serializers.IntegerField(read_only=True)
    volunteers_remaining = serializers.IntegerField(read_only=True)

    def get_organization_name(self, obj):
        """Поддерживает проекты от admin/moderator (без organization_profile)."""
        org = obj.organization
        profile = getattr(org, 'organization_profile', None)
        if profile:
            return profile.name
        # admin/moderator/пользователь без профиля — показываем username
        return org.username if org else ''
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'category', 'format', 'region',
            'start_date', 'end_date', 'volunteers_needed', 'status',
            'organization_name', 'volunteers_count', 'volunteers_remaining',
            'created_at', 'image'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for project detail view."""
    category = CategorySerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    organization = serializers.SerializerMethodField()
    volunteers_count = serializers.IntegerField(read_only=True)
    volunteers_remaining = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'category', 'format', 'region',
            'start_date', 'end_date', 'volunteers_needed', 'status',
            'organization', 'volunteers_count', 'volunteers_remaining',
            'is_active',
            'created_at', 'updated_at', 'image', 'requirements', 'contact_info'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'organization', 'volunteers_count', 'volunteers_remaining', 'is_active']

    def get_organization(self, obj: Project) -> Dict[str, Any]:
        """Get organization profile information."""
        if hasattr(obj.organization, 'organization_profile'):
            profile = obj.organization.organization_profile
            return {
                'id': obj.organization.id,
                'name': profile.name,
                'organization_type': profile.organization_type,
                'is_verified': profile.is_verified,
            }
        return {'id': obj.organization.id, 'name': obj.organization.username}


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating projects."""
    category_id = serializers.IntegerField(write_only=True)
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'category' in data and 'category_id' not in data:
            data['category_id'] = data.get('category')
        if 'region' in data and 'region_id' not in data:
            data['region_id'] = data.get('region')
        return super().to_internal_value(data)
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category_id', 'format', 'region_id',
            'start_date', 'end_date', 'volunteers_needed', 'status',
            'image', 'requirements', 'contact_info'
        ]

    def validate_category_id(self, value):
        """Validate that category exists."""
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Category does not exist.")
        return value

    def validate_region_id(self, value):
        """Validate that region exists if provided."""
        if value is not None and not Region.objects.filter(id=value).exists():
            raise serializers.ValidationError("Region does not exist.")
        return value

    def validate(self, attrs):
        """Validate project dates."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return attrs

    def create(self, validated_data):
        """Create project and set organization from request user."""
        category_id = validated_data.pop('category_id')
        region_id = validated_data.pop('region_id', None)
        
        project = Project.objects.create(
            category_id=category_id,
            region_id=region_id,
            organization=self.context['request'].user,
            **validated_data
        )
        return project

    def update(self, instance, validated_data):
        """Update project."""
        category_id = validated_data.pop('category_id', None)
        region_id = validated_data.pop('region_id', None)
        
        if category_id:
            instance.category_id = category_id
        if region_id is not None:
            instance.region_id = region_id
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
