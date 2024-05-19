from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
class CartResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data, extra=None):
        response_data = {
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        }
        if extra:
            response_data.update(extra)
        return Response(response_data)