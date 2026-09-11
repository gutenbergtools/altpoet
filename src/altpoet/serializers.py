from django.contrib.auth.models import User

from rest_framework import serializers


from altpoet.models import Document, Img, Image, Alt, Agent, UserSubmission


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['url', 'x', 'y', 'filesize']


class AltSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name')
    
    img = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='img_id')

    class Meta:
        model = Alt
        fields = ['id', 'img', 'text', 'source', 'votes', 'user_sub', 'created']


class ImgSerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=False, read_only=True)
    alt = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, allow_null=True, queryset=Alt.objects.all())
    alts = AltSerializer(many=True, read_only=True)

    class Meta:
        model = Img
        fields = ['id', 'image', 'img_id', 'img_type', 'is_figure', 'alt', 'alts']


class DocumentSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    imgs = ImgSerializer(many=True, read_only=True)
    status = serializers.CharField(source='get_status_display')
    detail = serializers.SerializerMethodField()
    _detail = ''
    def get_detail(self, obj):
            return self._detail or "ok"

    class Meta:
        model = Document
        fields = ['project', 'id', 'item', 'status', 'base', 'imgs', 'detail']

class UserSubmissionSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name')
    
    alts_created = AltSerializer(many=True, read_only=True)
    
    document = serializers.SlugRelatedField(many=False, read_only=True, slug_field='item')


    class Meta:
        model = UserSubmission
        fields = ['id', 'source', 'document', 'alts_created', 'created']
        
