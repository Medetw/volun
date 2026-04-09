from django_ratelimit import ALL
from django_ratelimit.core import is_ratelimited
from rest_framework import status
from rest_framework.response import Response

from apps.core.logging import security_logger, get_client_ip


class RateLimitMiddleware:
    """Middleware to apply rate limiting to API endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def _log_rate_limit(self, request, group):
        """Log rate limit violation."""
        ip = get_client_ip(request)
        security_logger.security_event(
            event="RATE_LIMIT_EXCEEDED",
            user_id=getattr(request.user, 'id', None) if hasattr(request, 'user') and hasattr(request.user, 'id') else None,
            ip_address=ip,
            details={'path': request.path, 'method': request.method, 'group': group}
        )

    def __call__(self, request):
        # Apply rate limiting to API endpoints
        if request.path.startswith('/api/'):
            # Different limits for different endpoints
            if request.path.startswith('/api/auth/'):
                # Stricter limits for auth endpoints
                login_path = request.path.startswith('/api/auth/login/')
                register_path = request.path.startswith('/api/auth/register/')
                if login_path or register_path:
                    if is_ratelimited(
                        request=request,
                        key='ip',
                        rate='5/m',  # 5 requests per minute
                        method=ALL,
                        increment=True,
                        group='auth_login_register'
                    ):
                        self._log_rate_limit(request, 'auth_login_register')
                        return Response(
                            {
                                'error': 'Too many authentication attempts. '
                                'Please try again later.'
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )
                else:
                    # Other auth endpoints
                    if is_ratelimited(
                        request=request,
                        key='ip',
                        rate='20/m',  # 20 requests per minute
                        method=ALL,
                        increment=True,
                        group='auth_other'
                    ):
                        self._log_rate_limit(request, 'auth_other')
                        return Response(
                            {'error': 'Rate limit exceeded for auth endpoints.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )

            elif request.path.startswith('/api/applications/'):
                # Application creation limits
                if request.method == 'POST':
                    if is_ratelimited(
                        request=request,
                        key='user',
                        rate='10/h',  # 10 applications per hour per user
                        method=ALL,
                        increment=True,
                        group='applications_create'
                    ):
                        self._log_rate_limit(request, 'applications_create')
                        return Response(
                            {
                                'error': 'Too many applications submitted. '
                                'Please wait before submitting more.'
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )

            elif request.path.startswith('/api/projects/'):
                # Project creation limits
                if request.method == 'POST':
                    if is_ratelimited(
                        request=request,
                        key='user',
                        rate='5/h',  # 5 projects per hour per organization
                        method=ALL,
                        increment=True,
                        group='projects_create'
                    ):
                        self._log_rate_limit(request, 'projects_create')
                        return Response(
                            {
                                'error': 'Too many projects created. '
                                'Please wait before creating more.'
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )

            # General API rate limiting
            else:
                if is_ratelimited(
                    request=request,
                    key='ip',
                    rate='100/m',  # 100 requests per minute per IP
                    method=ALL,
                    increment=True,
                    group='api_general'
                ):
                    self._log_rate_limit(request, 'api_general')
                    return Response(
                        {
                            'error': 'Rate limit exceeded. '
                            'Please slow down your requests.'
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

        response = self.get_response(request)
        return response
