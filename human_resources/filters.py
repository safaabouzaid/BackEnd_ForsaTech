import django_filters
from .models import Company
class CompaniesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    keyword=django_filters.filters.CharFilter(field_name="name",lookup_expr="icontains")
    class Meta:
        model = Company
        #fields = ['name','keyword']
        fields = ('name','keyword')

