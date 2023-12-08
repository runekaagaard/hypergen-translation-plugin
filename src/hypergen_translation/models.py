from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars

class String(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    value = models.TextField()

    def __str__(self):
        return truncatechars(self.value, 40)

    class Meta:
        verbose_name = "String"
        verbose_name_plural = "Strings"

class Occurrence(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    string = models.ForeignKey(String, on_delete=models.PROTECT)
    file_path = models.CharField(max_length=1024)
    python_path = models.CharField(max_length=1024)
    line_number = models.IntegerField()

    class Meta:
        verbose_name = "Occurrence"
        verbose_name_plural = "Occurrences"
        unique_together = ('string', 'file_path', 'line_number')

    def __str__(self):
        return f"{self.file_path}:{self.line_number}"

class Language(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    language_code = models.CharField(max_length=2)

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        return self.language_code

class Translation(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey('auth.User', related_name='translations_added', on_delete=models.PROTECT,
                                 null=True, blank=True)
    updated_by = models.ForeignKey('auth.User', related_name='translations_updated', on_delete=models.PROTECT,
                                   null=True, blank=True)
    string = models.ForeignKey(String, on_delete=models.PROTECT)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    value = models.TextField()

    class Meta:
        verbose_name = "Translation"
        verbose_name_plural = "Translations"

    def __str__(self):
        return truncatechars(self.value, 40)

@receiver(post_save, sender=Translation)
def post_save_translation(sender, instance, **kwargs):
    from hypergen_translation import api
    api.set_translations()
