from django.contrib.admin import SimpleListFilter

# Custom filter class
class HasOccurrenceFilter(SimpleListFilter):
    title = 'has occurrences'
    parameter_name = 'has_occurrences'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(occurrence__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.exclude(occurrence__isnull=False)
