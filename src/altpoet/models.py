from urllib.parse import urljoin

from django.conf import settings
from django.db import models
from django.utils import timezone

from django.utils.translation import gettext_lazy as _

from altpoet.ai import ai_alts

class Project(models.Model):
    ''' for example, Project Gutenberg. The Project object holds constants that otherwise would
    have to be repeated in every Document. For example, you could have a "local" object to work
    with files on your machine, or a "DP Canada" to work with their files. We're not coding 
    anything yet for EPUB files, but this object might be useful to represent an EPUB'''
    
    # for example, "Project Gutenberg"
    name = models.CharField(max_length=80, null=False, default="")

    # for example, "https://www.gutenberg.org"
    url = models.CharField(max_length=80, unique=True)

    # a template string for example, "/cache/epub/{item}/pg{item}-images.html"
    basepath = models.CharField(max_length=80, default="/{item)")
    
    def __str__(self):
        return self.name

class Document(models.Model):
    ''' (HTML) representation of a book or a webpage '''

    #a project that the document is part of. if null, then the item must 
    project = models.ForeignKey("Project", null=True, related_name='documents',
        on_delete=models.SET_NULL)

    # the identifier within the project. Or the full URL if no project
    # for Project Gutenberg, item is the Project Gutenberg ID
    item = models.CharField(max_length=80, default="")
    
    # a url set by the base of the Document (img src is  relative to this base, which is absolute
    base = models.CharField(max_length=80, default="")
    
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    # when preferred alt text last changed; ebookmaker polls on this
    alts_updated = models.DateTimeField(default=timezone.now, db_index=True)

    lang = models.CharField(max_length=10, default="en")

    NO_PROGRESS = 0
    IN_PROGRESS = 1
    COMPLETE = 2
    statuses = [(NO_PROGRESS, "No Progress"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETE, "Complete"),]

    status = models.IntegerField(
        choices=statuses,
        default=IN_PROGRESS
    )

    review_urgency = models.IntegerField(default=0)

    @property
    def url(self):
        if self.project:
            return urljoin(self.project.url, self.project.basepath % {'item':self.item})
        return self.base
    
    def add_ai_alts(self):
        return ai_alts(self)

    def __str__(self):
        return f'{self.item} in {self.project}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'item'], name="doc_unique_in_project"),
        ]

        permissions = [
            ("change_submission_status_tier_one", "Can change the status of this document if submitted by tier 0 (volunteer, non-staff)"),
            ("change_submission_status_tier_two", "Can always change the status of this document")
        ]
    
class Img(models.Model):
    """ This is an img element in an HTML document.
    """
    # document that contains the image
    document = models.ForeignKey("Document", null=False, related_name='imgs',
        on_delete=models.CASCADE)

    # 
    image = models.ForeignKey("Image", null=True, related_name='images', on_delete=models.SET_NULL)


    # the id set on the img element
    img_id = models.CharField(max_length=80, null=False)

    # whether the associated image is normal (0), purely decorative (1), a cover (2),  
    # button (3), other? (-1)
    img_type = models.IntegerField(default=0)

    # whether the associated image is inside a figure element.
    is_figure = models.BooleanField(default=False)
    
    # if the associated image is described by something else. If so, an id
    described_by = models.CharField(max_length=80, null=True)

    # this is the preferred alt
    alt = models.ForeignKey("Alt", null=True, related_name='imgs', on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.img_id} in {self.document}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['document', 'img_id'], name="img_unique_in_doc"),
        ]

        permissions = [
            ("set_preferred_alt", "Can set the preferred alt text for this image")
        ]

class Image(models.Model):
    """ This deals with image file, to allow multiple references to the same image.
    The hash allows us to identify duplicate images used across documents - I've seen hundreds of
    references to the same image in some collections. Often these are images of single characters,
    buttons or decorative images.
    """
    # always absolute
    url = models.CharField(max_length=1024, unique=True)
    
    # image dimensions (pixels)
    x = models.IntegerField(null=True)
    y = models.IntegerField(null=True)
    
    # filesize
    filesize = models.IntegerField(null=True)
    
    # hash of the image
    hash = models.CharField(max_length=64, null=True)
        
    def __str__(self):
        return self.url

    class Meta:
        indexes = [
            models.Index(fields=["hash"]),
        ]

class UserAltVote(models.Model):
    """Relation table between users and alts to keep track of votes
    """

    user = models.ForeignKey("Agent", null=False, related_name='voter', on_delete=models.CASCADE)

    alt = models.ForeignKey("Alt", null=False, related_name='alt_voted',  on_delete=models.CASCADE)

    UPVOTE = "UP"
    DOWNVOTE = "DN"
    NONEVOTE = "NO"
    VOTE_CHOICES = [(UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote"),
        (NONEVOTE, "No vote"),]

    vote = models.CharField(
        max_length=2,
        choices=VOTE_CHOICES,
        default=NONEVOTE
    )

    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=['user', 'alt'], name="alt_vote_unique_per_user"),
            ]

# add unique constraint to tuple (user, image, document)
# one submission per image in document
class Alt(models.Model):
    """This model represents alt text entries and proposed alt text entries
    """
    # alt text for the image
    text = models.CharField(max_length=2000, default="")

    # 
    votes = models.IntegerField(default=0, null=False)
    
    # the img that this alt-text pertains to
    img = models.ForeignKey("Img", null=True, related_name='alts',  on_delete=models.CASCADE)
    
    # where did the alt text come from? if null, it came with the document
    source = models.ForeignKey("Agent", null=True, related_name='alts',  on_delete=models.SET_NULL)

    user_sub = models.ForeignKey("UserSubmission", null=True, blank=True,
                                 related_name='alts_created', on_delete=models.SET_NULL)
    
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'alt for {self.img} in {self.img.document}'
    
    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=['img', 'source'], name="alt_unique_per_user"),
            ]


class Agent(models.Model):
    """This model represents creators of alt text. Could be a person, (a user) 
    or perhaps an AI, in which case user could be null.
    """
    # entity supplying the alt text
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, related_name='agents')    

    name = models.CharField(max_length=80, null=True) 

    created = models.DateTimeField(auto_now_add=True, db_index=True)


# email eric / pull request when figuring out how/if to parse json in database
class UserSubmission(models.Model):
    """This model is a user's saved submission of alt texts that they have written and plan
    to submit later for voting and approval. Always POSTed by real users, not AI.
    """

    source = models.ForeignKey("Agent", null=False, related_name='user_who_submitted', on_delete=models.CASCADE)
    
    document = models.ForeignKey("Document", null=False, related_name='related_document',
        on_delete=models.CASCADE)
    
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'user submission for {self.document} by {self.source}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['document', 'source'], name="unique_submission"),
        ]
