from django.contrib import admin
from django.conf import settings
from django.utils.safestring import mark_safe

from .models import String, Occurrence, Language, Translation
from .filters import HasOccurrenceFilter, HasTranslationFilter

class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    readonly_fields = ('list_file_path', 'python_path', 'line_number', 'added', 'updated')
    fields = readonly_fields
    extra = 0
    can_delete = False

    def list_file_path(self, obj):
        if getattr(settings, 'HYPERGEN_TRANSLATION_GITHUB', None):
            github_url = f"{settings.HYPERGEN_TRANSLATION_GITHUB}/blob/main/{obj.file_path}#L{obj.line_number}"
            return mark_safe(f'<a href="{github_url}" target="_blank">{obj.file_path}</a>')
        else:
            return obj.file_path

    list_file_path.short_description = "File Path"

class TranslationInline(admin.TabularInline):
    model = Translation
    readonly_fields = ('added', 'updated', 'added_by', 'updated_by')
    extra = 0

class StringAdmin(admin.ModelAdmin):
    list_display = ('value', 'added', 'updated')
    readonly_fields = ('value', 'added', 'updated')
    inlines = [TranslationInline, OccurrenceInline]
    search_fields = ('value',)
    list_filter = (HasTranslationFilter, HasOccurrenceFilter, 'added', 'updated')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Translation):
                if not instance.pk:  # Checking if the instance is being created
                    instance.added_by = request.user
                else:
                    instance.updated_by = request.user
                instance.save()
        formset.save_m2m()  # For many-to-many relationships

admin.site.register(String, StringAdmin)

class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ('string', 'file_path', 'python_path', 'line_number', 'added', 'updated')
    readonly_fields = list_display
    search_fields = ("file_path", "python_path", "string__value")
    list_filter = ("file_path",)

admin.site.register(Occurrence, OccurrenceAdmin)

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language_code', 'added', 'updated')
    readonly_fields = ('added', 'updated')

admin.site.register(Language, LanguageAdmin)

class TranslationAdmin(admin.ModelAdmin):
    list_display = ('string', 'language', 'added', 'updated', 'added_by', 'updated_by')
    list_filter = ("added", "updated")
    readonly_fields = ('added', 'updated', 'added_by', 'updated_by')
    search_fields = ('value',)

admin.site.register(Translation, TranslationAdmin)
