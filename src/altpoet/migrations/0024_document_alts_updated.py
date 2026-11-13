from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('altpoet', '0023_document_review_urgency'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='alts_updated',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
