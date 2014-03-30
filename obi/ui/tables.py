import django_tables2 as tables
from ui.models import Search


class SearchTable(tables.Table):
    class Meta:
        model = Search
        attrs = {"class": "paleblue"}

    # to enhance search privacy, we only
    # display the date, not the time
    def render_date_searched(self, value):
        return value.date
