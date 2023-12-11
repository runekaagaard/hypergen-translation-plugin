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
    list_display = ('original_value', 'translations')
    readonly_fields = ('value', 'added', 'updated')
    inlines = [TranslationInline, OccurrenceInline]
    search_fields = ('value', 'translation__value')
    list_filter = (HasTranslationFilter, HasOccurrenceFilter, 'added', 'updated')

    def save_formset(self, request, form, formset, *args, **kwargs):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Translation):
                if not instance.pk:
                    instance.added_by = request.user
                else:
                    instance.updated_by = request.user

        return super().save_formset(request, form, formset, *args, **kwargs)

    def original_value(self, obj):
        return str(obj)

    def translations(self, obj):
        return mark_safe("<br >".join(
            f"<b>{x.language.language_code}: </b>{str(x)}" for x in obj.translation_set.all()))

admin.site.register(String, StringAdmin)

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language_code',)
    readonly_fields = ('added', 'updated')

admin.site.register(Language, LanguageAdmin)

class TranslationAdmin(admin.ModelAdmin):
    list_display = ('string', 'language', 'value')
    list_editable = ('value',)
    list_filter = ("language", "added", "updated")
    readonly_fields = ('added', 'updated', 'added_by', 'updated_by')
    search_fields = ('value', 'string__value')

admin.site.register(Translation, TranslationAdmin)
