"""
Кастомные утилиты логирования для волонтерской платформы
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

# Получаем настроенные логгеры
django_logger = logging.getLogger('django')
apps_logger = logging.getLogger('apps')
error_logger = logging.getLogger('django.request')


class PlatformLogger:
    """Удобный логгер для платформы"""
    
    def __init__(self, name: str = None):
        self.logger = logging.getLogger(name) if name else apps_logger
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Информационное сообщение"""
        self.logger.info(message, extra=extra or {})
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Отладочное сообщение"""
        self.logger.debug(message, extra=extra or {})
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Предупреждение"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, exception: Exception = None, extra: Dict[str, Any] = None):
        """Ошибка с трейсбеком"""
        if exception:
            message += f"\nException: {str(exception)}"
            message += f"\nTraceback: {traceback.format_exc()}"
        self.logger.error(message, extra=extra or {})
    
    def api_request(self, method: str, endpoint: str, user_id: int = None, 
                   status_code: int = None, duration: float = None):
        """Логирование API запросов"""
        message = f"API {method} {endpoint}"
        if user_id:
            message += f" | User: {user_id}"
        if status_code:
            message += f" | Status: {status_code}"
        if duration:
            message += f" | Duration: {duration:.3f}s"
        
        self.info(message, {
            'type': 'api_request',
            'method': method,
            'endpoint': endpoint,
            'user_id': user_id,
            'status_code': status_code,
            'duration': duration
        })
    
    def user_action(self, action: str, user_id: int, details: Dict[str, Any] = None):
        """Логирование действий пользователя"""
        message = f"User Action: {action} | User: {user_id}"
        if details:
            message += f" | Details: {details}"
        
        self.info(message, {
            'type': 'user_action',
            'action': action,
            'user_id': user_id,
            'details': details or {}
        })
    
    def system_event(self, event: str, details: Dict[str, Any] = None):
        """Логирование системных событий"""
        message = f"System Event: {event}"
        if details:
            message += f" | Details: {details}"
        
        self.info(message, {
            'type': 'system_event',
            'event': event,
            'details': details or {}
        })
    
    def security_event(self, event: str, user_id: int = None, 
                      ip_address: str = None, details: Dict[str, Any] = None):
        """Логирование событий безопасности"""
        message = f"SECURITY: {event}"
        if user_id:
            message += f" | User: {user_id}"
        if ip_address:
            message += f" | IP: {ip_address}"
        if details:
            message += f" | Details: {details}"
        
        self.warning(message, {
            'type': 'security_event',
            'event': event,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        })


# Глобальные экземпляры логгеров
logger = PlatformLogger('apps')
security_logger = PlatformLogger('apps.security')
api_logger = PlatformLogger('apps.api')


def log_api_request(view_func):
    """Декоратор для логирования API запросов"""
    def wrapper(request, *args, **kwargs):
        start_time = datetime.now()
        
        # Логируем начало запроса
        logger.api_request(
            method=request.method,
            endpoint=request.get_full_path(),
            user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') else None
        )
        
        try:
            response = view_func(request, *args, **kwargs)
            
            # Логируем завершение запроса
            duration = (datetime.now() - start_time).total_seconds()
            logger.api_request(
                method=request.method,
                endpoint=request.get_full_path(),
                user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                status_code=getattr(response, 'status_code', None),
                duration=duration
            )
            
            return response
        except Exception as e:
            # Логируем ошибку
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"API request failed: {request.method} {request.get_full_path()}",
                exception=e,
                extra={
                    'method': request.method,
                    'endpoint': request.get_full_path(),
                    'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                    'duration': duration
                }
            )
            raise
    
    return wrapper


def get_client_ip(request) -> str:
    """Получить IP адрес клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_authentication_attempt(request, success: bool, username: str = None):
    """Логирование попыток аутентификации"""
    ip = get_client_ip(request)
    event = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
    
    security_logger.security_event(
        event=event,
        user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') and success else None,
        ip_address=ip,
        details={'username': username}
    )


def log_permission_denied(request, permission: str):
    """Логирование отказа в доступе"""
    ip = get_client_ip(request)
    
    security_logger.security_event(
        event="PERMISSION_DENIED",
        user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
        ip_address=ip,
        details={'permission': permission, 'path': request.get_full_path()}
    )
