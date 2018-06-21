from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


# curl -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkaUBhZGkuY29tIiwiZXhwIjoxNTI5NTc4NTI4LCJlbWFpbCI6ImFkaUBhZGkuY29tIn0.29gqJX1jcobitZQzVA8wqn39RW8wmgItSnB24ZqdwV8" http://localhost:8000/api/vehicles/