
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Agent, Alt, Document, Img

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Agent.objects.create(user=instance, name=instance.username)

def _mark_document_alts_updated(document_id):
    Document.objects.filter(pk=document_id).update(alts_updated=timezone.now())

# post_save alone can't see the old value, so stash it first
@receiver(pre_save, sender=Img)
def stash_old_preferred_alt(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_alt_id = None
        return
    instance._old_alt_id = (
        Img.objects.filter(pk=instance.pk).values_list('alt_id', flat=True).first())

# preferred alt was assigned or changed (approval)
@receiver(post_save, sender=Img)
def on_preferred_alt_assigned(sender, instance, **kwargs):
    if getattr(instance, '_old_alt_id', None) != instance.alt_id:
        _mark_document_alts_updated(instance.document_id)

# preferred alt's text was edited
@receiver(post_save, sender=Alt)
def on_preferred_alt_text_edited(sender, instance, **kwargs):
    if instance.img_id and instance.img.alt_id == instance.pk:
        _mark_document_alts_updated(instance.img.document_id)
