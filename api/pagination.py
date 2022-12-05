from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class FifteenItemsPagination(PageNumberPagination):
    page_size = 10


class EntityPagination(FifteenItemsPagination):
    category_data = None

    def get_paginated_response(self, data):
        if hasattr(self, "category_data"):
            self.category_data = getattr(self, "category_data")
        return Response(OrderedDict([
            ("count", self.page.paginator.count),
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            ("results", data),
	    ("total_pages", self.page.paginator.num_pages),
	    ("page_number", self.page.number),
	    ("per_page", self.page.paginator.per_page),
            ("category", self.category_data)
        ]))
