from django_filters import FilterSet, CharFilter, NumberFilter

from reviews.models import Title


class TitleFilterSet(FilterSet):
    name = CharFilter(field_name='name')
    year = NumberFilter(field_name='year')
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')
