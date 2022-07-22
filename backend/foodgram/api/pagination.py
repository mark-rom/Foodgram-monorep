from rest_framework.pagination import PageNumberPagination


class PageNumberLimitPagination(PageNumberPagination):
    """Custom pagination class inherited from PageNumberPagination.
    Page_size_query_param overriden to "limit"."""

    page_size_query_param = 'limit'
