from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.news.models import News, NewsCategory, NewsStatus

User = get_user_model()


class NewsModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password',
            role='admin'
        )
        
        self.news = News.objects.create(
            title='Тестовая новость',
            slug='test-news',
            content='Содержание тестовой новости',
            excerpt='Краткое описание',
            category=NewsCategory.GENERAL,
            status=NewsStatus.PUBLISHED,
            author=self.admin_user
        )

    def test_news_creation(self):
        """Тест создания новости."""
        self.assertEqual(self.news.title, 'Тестовая новость')
        self.assertEqual(self.news.status, NewsStatus.PUBLISHED)
        self.assertEqual(self.news.author, self.admin_user)

    def test_news_str_method(self):
        """Тест __str__ метода."""
        self.assertEqual(str(self.news), 'Тестовая новость')

    def test_is_published_property(self):
        """Тест свойства is_published."""
        self.assertTrue(self.news.is_published)
        
        self.news.status = NewsStatus.DRAFT
        self.news.save()
        self.assertFalse(self.news.is_published)

    def test_reading_time_calculation(self):
        """Тест расчета времени чтения."""
        # ~200 слов = 1 минута
        self.news.content = 'word ' * 200
        self.news.save()
        self.assertEqual(self.news.reading_time, 1)
        
        # ~400 слов = 2 минуты
        self.news.content = 'word ' * 400
        self.news.save()
        self.assertEqual(self.news.reading_time, 2)

    def test_increment_views(self):
        """Тест увеличения счетчика просмотров."""
        initial_views = self.news.views_count
        self.news.increment_views()
        self.assertEqual(self.news.views_count, initial_views + 1)
