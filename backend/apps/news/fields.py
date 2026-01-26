from rest_framework import serializers


class NewsCategoryField(serializers.ReadOnlyField):
    """Поле для отображения категории новости."""
    
    def to_representation(self, value):
        if value == 'general':
            return 'Общие новости'
        elif value == 'events':
            return 'Мероприятия'
        elif value == 'announcements':
            return 'Объявления'
        elif value == 'success_stories':
            return 'Истории успеха'
        elif value == 'partners':
            return 'Партнеры'
        return value


class NewsStatusField(serializers.ReadOnlyField):
    """Поле для отображения статуса новости."""
    
    def to_representation(self, value):
        if value == 'draft':
            return 'Черновик'
        elif value == 'published':
            return 'Опубликовано'
        elif value == 'archived':
            return 'Архив'
        return value
