from django.contrib.admin import SimpleListFilter

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

class HasTranslationFilter(SimpleListFilter):
    title = 'has translations'
    parameter_name = 'has_translations'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(translation__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.exclude(translation__isnull=False)
