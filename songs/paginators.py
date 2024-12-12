from rest_framework.pagination import LimitOffsetPagination

class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10  # Default limit if none is specified
    max_limit = 25  # Maximum limit allowed