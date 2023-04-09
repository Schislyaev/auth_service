from opentelemetry import trace

from core.settings import settings


def tracer(name='span'):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if settings.tracer:
                tracer_obj = trace.get_tracer(__name__)
                with tracer_obj.start_as_current_span(name):
                    function(*args, **kwargs)
        return wrapper
    return decorator


def class_tracer(name='span'):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            if settings.tracer:
                tracer_obj = trace.get_tracer(__name__)
                with tracer_obj.start_as_current_span(name):
                    result = function(self, *args, **kwargs)
                    return result
        return wrapper
    return decorator
