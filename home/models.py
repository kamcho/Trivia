import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class TimeStampedModel(models.Model):
    """
    Abstract base model with created and updated timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ChurchCategory(TimeStampedModel):
    """
    Represents the denomination or category of a church (e.g., Protestant, Catholic).
    """
    categories = [
        ('Pentecostal', 'Pentecostal'),
        ('Charismatic', 'Charismatic'),
        ('Evangelical', 'Evangelical'),
        ('Baptist', 'Baptist'),
        ('Methodist', 'Methodist'),
        ('Catholic', 'Catholic'),
        ('Orthodox', 'Orthodox'),
        ('Protestant', 'Protestant'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100, unique=True, choices=categories)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Church Category"
        verbose_name_plural = "Church Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Church(TimeStampedModel):
    """
    Represents a church that participates in the trivia platform.
    """
    uuid = models.UUIDField(default=uuid.uuid4,unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        ChurchCategory,
        on_delete=models.PROTECT,
        related_name='churches'
    )
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='church_logos/', blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_churches',
        help_text='User who manages/created this church'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TriviaGroup(TimeStampedModel):
    """
    Represents a trivia group that competes on behalf of a church.
    """
    category = [
        ('Adults', 'Adults'),
        ('Youth', 'Youth'),
        ('Children', 'Children'),
        ('Senior', 'Senior'),
        ('Junior', 'Junior'),
        ('Teens', 'Teens'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=category)
    church = models.ForeignKey(
        Church,
        on_delete=models.CASCADE,
        related_name='trivia_groups'
    )
    description = models.TextField(blank=True, null=True)
    max_members = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    
    patron = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patroned_groups')
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='captained_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='trivia_groups')
    # Competition stats
    total_competitions = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['church__name', 'name']
        unique_together = ['church', 'name']
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["church", "is_active"]),
            models.Index(fields=["category"]),
        ]
        verbose_name = "Trivia Group"
        verbose_name_plural = "Trivia Groups"

    def __str__(self):
        return f"{self.name} ({self.church.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.church.name}-{self.name}")
            self.slug = base_slug
        super().save(*args, **kwargs)
    
    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        if self.total_competitions == 0:
            return 0
        return round((self.wins / self.total_competitions) * 100, 1)


class QuestionCategory(TimeStampedModel):
    """
    Represents categories for trivia questions (e.g., Old Testament, New Testament, Church History).
    """
    category_choices = [
        ('Old Testament', 'Old Testament'),
        ('New Testament', 'New Testament'),
        ('Church History', 'Church History'),
        ('General Knowledge', 'General Knowledge'),
        ('Other', 'Other'),

    ]
    name = models.CharField(max_length=100, unique=True, choices=category_choices)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Question Category"
        verbose_name_plural = "Question Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Question(TimeStampedModel):
    """
    Represents a trivia question with multiple choice answers.
    """
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    QUESTION_TYPE_CHOICES = [
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Select'),
        ('open', 'Open Ended'),
    ]
    
    level_category = [
        ('Adults', 'Adults'),
        ('Youth', 'Youth'),
        ('Children', 'Children'),
        ('Senior', 'Senior'),
        ('Junior', 'Junior'),
        ('Teens', 'Teens'),
        ('All', 'All'),
    ]
    level = models.CharField(max_length=100, choices=level_category, default='All')
    # New: allow selecting multiple applicable levels
    allowed_levels = models.JSONField(
        default=list,
        blank=True,
        help_text="Select one or more levels this question applies to"
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    categories = models.ManyToManyField(
        QuestionCategory,
        related_name='questions',
        blank=True,
    )
    activities = models.ManyToManyField(
        'CompetitionActivity',
        related_name='questions',
        blank=True,
        help_text='Activities this question is associated with'
    )
    question_text = models.TextField()
    
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Medium')
    # Indicates how responses should be collected/validated for this question
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='single')
    explanation = models.TextField(
        blank=True, 
        help_text="Optional explanation for the correct answer"
    )
    bible_reference = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Bible verse reference (e.g., John 3:16)"
    )
    points = models.PositiveIntegerField(
        default=1, 
        help_text="Points awarded for correct answer"
    )
    penalty = models.PositiveIntegerField(
        default=1,
        help_text="If 0, allow positive proportional credit for multiple-select; otherwise full-or-nothing"
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_questions'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["difficulty"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_by"]),
        ]
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"{self.question_text[:50]}..." if len(self.question_text) > 50 else self.question_text

    def get_choices(self):
        choices = Choice.objects.filter(question__id=self.id)
    
   
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['is_correct', 'choice_text']
        indexes = [
            models.Index(fields=["question", "is_correct"]),
        ]
        verbose_name = "Choice"
        verbose_name_plural = "Choices" 

    def __str__(self):
        return str(self.choice_text)


class Cohort(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_cohorts')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.name)
    

class ActivityCategory(models.Model):
    categories = [
        ('Online', 'Online'),
        ('Stage', 'Stage'),
    ]
    name = models.CharField(max_length=100, choices=categories)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_competition_categories')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.name)


class CompetitionActivity(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(
        ActivityCategory,
        related_name='activities',
        blank=True
    )
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ActivityInstruction(TimeStampedModel):
    """
    Step-by-step instruction items for how a `CompetitionActivity` should be conducted.
    """
    activity = models.ForeignKey(
        CompetitionActivity,
        on_delete=models.CASCADE,
        related_name='instructions'
    )
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=["activity", "order"]),
            models.Index(fields=["is_active"]),
        ]
        verbose_name = 'Activity Instruction'
        verbose_name_plural = 'Activity Instructions'
        constraints = [
            models.UniqueConstraint(fields=['activity', 'order'], name='uniq_instruction_activity_order')
        ]

    def __str__(self):
        return f"Instruction #{self.order} for {self.activity.name}"


class ActivityRule(TimeStampedModel):
    """
    Rules and regulations that govern a `CompetitionActivity`.
    """
    activity = models.ForeignKey(
        CompetitionActivity,
        on_delete=models.CASCADE,
        related_name='rules'
    )
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=["activity", "order"]),
            models.Index(fields=["is_active"]),
        ]
        verbose_name = 'Activity Rule'
        verbose_name_plural = 'Activity Rules'
        constraints = [
            models.UniqueConstraint(fields=['activity', 'order'], name='uniq_rule_activity_order')
        ]

    def __str__(self):
        return f"Rule #{self.order} for {self.activity.name}"


class Competition(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    activities = models.ManyToManyField(CompetitionActivity, related_name='competitions')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_competitions')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        # Ensure slug is generated from name if not provided
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def status(self):
        """Calculate competition status based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.start_date > today:
            return 'upcoming'
        elif self.start_date <= today <= self.end_date:
            return 'active'
        else:
            return 'past'
    
    def get_status_display(self):
        """Return human-readable status"""
        status_map = {
            'upcoming': 'Upcoming',
            'active': 'Active',
            'past': 'Past'
        }
        return status_map.get(self.status, 'Unknown')


class CompetitionMedia(TimeStampedModel):
    """
    Media associated with a Competition. Supports image, video file, or external URL/embed.
    If intro_media=True, it is shown before activities. Only one intro media per competition.
    """
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video File'),
        ('embed', 'External URL/Embed'),
    ]

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='media'
    )
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    image = models.ImageField(upload_to='competition_media/images/', blank=True, null=True)
    video = models.FileField(upload_to='competition_media/videos/', blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text='External media URL (e.g., YouTube)')
    intro_media = models.BooleanField(default=False, help_text='Show before activities (max 1 per competition)')
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        indexes = [
            models.Index(fields=["competition", "order"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['competition'],
                condition=Q(intro_media=True),
                name='uniq_intro_media_per_competition'
            )
        ]
        verbose_name = 'Competition Media'
        verbose_name_plural = 'Competition Media'

    def __str__(self):
        base = self.title or f"Media #{self.pk}" if self.pk else "Media"
        return f"{base} ({self.media_type})"

    def clean(self):
        """
        Validate field consistency:
        - Require at least one of image, video, or url
        - Enforce single source populated
        - Ensure media_type matches populated field
        """
        populated = [bool(self.image), bool(self.video), bool(self.url)]
        populated_count = sum(1 for v in populated if v)
        if populated_count == 0:
            raise models.ValidationError('Provide an image, a video, or an external URL for media.')
        if populated_count > 1:
            raise models.ValidationError('Only one of image, video, or URL should be set.')
        # Align media_type to the populated field
        if self.image and self.media_type != 'image':
            self.media_type = 'image'
        elif self.video and self.media_type != 'video':
            self.media_type = 'video'
        elif self.url and self.media_type != 'embed':
            self.media_type = 'embed'

    def save(self, *args, **kwargs):
        # Auto-derive media_type if mismatched or blank
        if self.image:
            self.media_type = 'image'
            self.video = None
            self.url = None
        elif self.video:
            self.media_type = 'video'
            self.image = None
            self.url = None
        elif self.url:
            self.media_type = 'embed'
            self.image = None
            self.video = None
        super().save(*args, **kwargs)


# --- Competition extended models ---

class CompetitionEligibility(TimeStampedModel):
    PARTICIPATION_CHOICES = [
        ('Individual', 'Individual'),
        ('Group', 'Group'),
        ('All', 'All'),
    ]
    LEVEL_CHOICES = [
        ('Adults', 'Adults'),
        ('Youth', 'Youth'),
        ('Children', 'Children'),
        ('Senior', 'Senior'),
        ('Junior', 'Junior'),
        ('Teens', 'Teens'),
        ('All', 'All'),
    ]

    competition = models.OneToOneField(Competition, on_delete=models.CASCADE, related_name='eligibility')
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    # One or more allowed levels (store as list of choice keys)
    allowed_levels = models.JSONField(default=list, blank=True, help_text='Select one or more levels')
    allowed_participation = models.CharField(max_length=20, choices=PARTICIPATION_CHOICES, default='All')
    
    prerequisites = models.TextField(blank=True)
    eligibility_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Competition Eligibility'
        verbose_name_plural = 'Competition Eligibility'

    def __str__(self):
        return f"Eligibility for {self.competition.name}"

    def get_allowed_levels_display(self):
        label_map = dict(self.LEVEL_CHOICES)
        # empty list or contains 'All' means all levels
        if not self.allowed_levels or 'All' in self.allowed_levels:
            return 'All'
        return ', '.join(label_map.get(v, v) for v in self.allowed_levels)


class CompetitionRegistrationWindow(TimeStampedModel):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='registration_windows')
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text='Leave blank for unlimited')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_currency = models.CharField(max_length=10, default='KES')
    terms_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['opens_at']
        verbose_name = 'Registration Window'
        verbose_name_plural = 'Registration Windows'

    def __str__(self):
        return f"Registration {self.opens_at:%Y-%m-%d} → {self.closes_at:%Y-%m-%d}"


class CompetitionBooking(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='competition_bookings')
    group = models.ForeignKey('TriviaGroup', on_delete=models.CASCADE, null=True, blank=True, related_name='competition_bookings')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    booked_at = models.DateTimeField(auto_now_add=True)
    # Payment fields
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, blank=True, choices=[
        ('mpesa', 'M-Pesa'),
        ('paypal_card', 'PayPal/Card'),
        ('none', 'None'),
    ], default='none')
    payment_status = models.CharField(max_length=20, blank=True, choices=[
        ('pending', 'Pending'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')
    payment_ref = models.CharField(max_length=100, blank=True)
    payment_receipt = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='KES')
    num_slots = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["competition", "status"]),
        ]
        verbose_name = 'Competition Booking'
        verbose_name_plural = 'Competition Bookings'

    def __str__(self):
        owner = self.user or self.group
        return f"Booking({self.status}) - {owner} - {self.competition.name}"

    def clean(self):
        if not self.user and not self.group:
            raise models.ValidationError('Either user or group must be set.')
        if self.user and self.group:
            raise models.ValidationError('Set either user or group, not both.')


class CompetitionContact(TimeStampedModel):
    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('support', 'Support'),
        ('press', 'Press'),
        ('other', 'Other'),
    ]
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('other', 'Other'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='organizer')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    preferred_channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='email')
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-is_primary', 'name']
        verbose_name = 'Competition Contact'
        verbose_name_plural = 'Competition Contacts'

    def __str__(self):
        return f"{self.name} ({self.role})"


class CompetitionVenue(TimeStampedModel):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='venues')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    map_link = models.URLField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    room = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Competition Venue'
        verbose_name_plural = 'Competition Venues'

    def __str__(self):
        return self.name


class CompetitionScheduleItem(TimeStampedModel):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='schedule_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location_hint = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=1)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_at', 'order']
        verbose_name = 'Schedule Item'
        verbose_name_plural = 'Schedule Items'

    def __str__(self):
        return f"{self.title} ({self.start_at:%Y-%m-%d %H:%M})"


class CompetitionSponsor(TimeStampedModel):
    TIER_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
        ('partner', 'Partner'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='sponsors')
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='competition_media/sponsors/', blank=True, null=True)
    website = models.URLField(blank=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='partner')
    blurb = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Competition Sponsor'
        verbose_name_plural = 'Competition Sponsors'

    def __str__(self):
        return f"{self.name} ({self.tier})"


class CompetitionPolicy(TimeStampedModel):
    POLICY_CHOICES = [
        ('refund', 'Refund Policy'),
        ('code', 'Code of Conduct'),
        ('privacy', 'Privacy'),
        ('other', 'Other'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='policies')
    policy_type = models.CharField(max_length=20, choices=POLICY_CHOICES, default='other')
    content = models.TextField()
    effective_date = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['policy_type', 'effective_date']
        verbose_name = 'Competition Policy'
        verbose_name_plural = 'Competition Policies'

    def __str__(self):
        return f"{self.get_policy_type_display()}"


class CompetitionFAQ(TimeStampedModel):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Competition FAQ'
        verbose_name_plural = 'Competition FAQs'

    def __str__(self):
        return self.question


class CompetitionResource(TimeStampedModel):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='competition_media/resources/', blank=True, null=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Competition Resource'
        verbose_name_plural = 'Competition Resources'

    def __str__(self):
        return self.title


class CompetitionSocialLink(TimeStampedModel):
    NETWORK_CHOICES = [
        ('facebook', 'Facebook'),
        ('x', 'X/Twitter'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('other', 'Other'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='social_links')
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES, default='other')
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Competition Social Link'
        verbose_name_plural = 'Competition Social Links'

    def __str__(self):
        return f"{self.network}: {self.url}"

class TestQuiz(TimeStampedModel):
    """
    Represents a test quiz that can be taken by users or groups.
    """
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    
    QUIZ_TYPE_CHOICES = [
        ('Practice', 'Practice'),
        ('Assessment', 'Assessment'),
        ('Competition', 'Competition'),
        ('Study', 'Study'),
    ]
    level_category = [
        ('Adults', 'Adults'),
        ('Youth', 'Youth'),
        ('Children', 'Children'),
        ('Senior', 'Senior'),
        ('Junior', 'Junior'),
        ('Teens', 'Teens'),
        ('All', 'All'),
    ]
    participation_category = [
        ('Individual', 'Individual'),
        ('Group', 'Group'),
        ('All', 'All'),
    ]
    participation = models.CharField(max_length=100, choices=participation_category, default='All')
    level = models.CharField(max_length=100, choices=level_category, default='All')
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Description of the quiz")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Medium')
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default='Practice')
    
    # Questions and categories
    questions = models.ManyToManyField(
        Question,
        related_name='test_quizzes',
        blank=True,
        help_text="Questions included in this quiz"
    )
    activities = models.ManyToManyField(
        CompetitionActivity,
        related_name='quizzes',
        blank=True,
        help_text="Activities this quiz is associated with"
    )
   
    
    # Quiz settings
    time_limit = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Time limit in minutes (null = no limit)"
    )
    max_attempts = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of attempts allowed"
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        help_text="Minimum score percentage to pass"
    )
    total_points = models.PositiveIntegerField(
        default=0,
        help_text="Total possible points for this quiz"
    )
    
    # Access control
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True, help_text="Available to all users")
    requires_authentication = models.BooleanField(default=True)
    
    # Creator and organization
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_test_quizzes'
    )

    
    # Instructions and metadata
    instructions = models.TextField(
        blank=True,
        help_text="Instructions for taking this quiz"
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional quiz settings and data"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["quiz_type"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["created_by"]),
        ]
        verbose_name = "Test Quiz"
        verbose_name_plural = "Test Quizzes"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def calculate_total_points(self):
        """Calculate total points based on questions"""
        return sum(question.points for question in self.questions.all())
    
    def get_question_count(self):
        """Get the number of questions in this quiz"""
        return self.questions.count()
    
    def get_estimated_duration(self):
        """Get estimated duration in minutes based on question count"""
        if self.time_limit:
            return self.time_limit
        # Estimate 1 minute per question if no time limit set
        return self.get_question_count()
    
    def is_available_to_user(self, user):
        """Check if quiz is available to a specific user"""
        if not self.is_active:
            return False
        
        if not self.is_public and not user.is_authenticated:
            return False
            
        if self.requires_authentication and not user.is_authenticated:
            return False
            
        return True


class TestQuizAttempt(TimeStampedModel):
    """Tracks an individual's attempt of a TestQuiz."""
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    quiz = models.ForeignKey(TestQuiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts', null=True, blank=True)
    attempt_number = models.PositiveIntegerField(default=1, help_text='Incremented per user per quiz')
    session_id = models.CharField(max_length=40, blank=True, null=True, help_text='for unauthenticated users')
    # Results
    score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='started')

    # Timestamps and duration
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

   

    class Meta:
        ordering = ['-created_at']
        unique_together = [('quiz', 'user', 'attempt_number')]
        indexes = [
            models.Index(fields=["quiz", "user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = 'Test Quiz Attempt'
        verbose_name_plural = 'Test Quiz Attempts'

    def __str__(self):
        return f"Attempt #{self.attempt_number} - {self.user} - {self.quiz.name}"


class GroupTestQuizAttempt(TimeStampedModel):
    """Tracks a TriviaGroup's attempt of a TestQuiz."""
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    quiz = models.ForeignKey(TestQuiz, on_delete=models.CASCADE, related_name='group_attempts')
    group = models.ForeignKey(TriviaGroup, on_delete=models.CASCADE, related_name='quiz_attempts')
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_group_quiz_attempts')
    attempt_number = models.PositiveIntegerField(default=1, help_text='Incremented per group per quiz')

    # Results
    score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='started')

    # Timestamps and duration
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('quiz', 'group', 'attempt_number')]
        indexes = [
            models.Index(fields=["quiz", "group"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
        verbose_name = 'Group Test Quiz Attempt'
        verbose_name_plural = 'Group Test Quiz Attempts'

    def __str__(self):
        return f"Attempt #{self.attempt_number} - {self.group} - {self.quiz.name}"


class UserResponse(TimeStampedModel):
    """
    Stores a user's response to a specific question within a TestQuizAttempt.
    Ensures one response per (attempt, question) and auto-evaluates correctness.
    """
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    attempt = models.ForeignKey(
        TestQuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_responses'
    )
 
    # Optional free-text answer for open-ended questions (if ever used)
    text_answer = models.TextField(blank=True, null=True)
    # Support multiple selections for multiple-select questions
    selected_choices = models.ManyToManyField(
        Choice,
        related_name='user_responses_selected',
        blank=True,
    )

    # Evaluation fields
    points_awarded = models.PositiveIntegerField(default=0)

    # Telemetry/extra data
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('attempt', 'question')]
        indexes = [
            models.Index(fields=["attempt", "question"]),
            models.Index(fields=["question",]),
        ]
        verbose_name = 'User Response'
        verbose_name_plural = 'User Responses'

    def __str__(self):
        return f"UserResponse({self.attempt_id}, Q={self.question_id})"

    

    


class GroupResponse(TimeStampedModel):
    """
    Stores a group's response to a specific question within a GroupTestQuizAttempt.
    Optionally tracks which user in the group provided the response.
    """
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    attempt = models.ForeignKey(
        GroupTestQuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    group = models.ForeignKey(TriviaGroup, on_delete=models.RESTRICT)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='group_responses'
    )
 
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_question_responses'
    )
    # Optional free-text answer for open-ended questions
    text_answer = models.TextField(blank=True, null=True)
    # Support multiple selections for multiple-select questions
    selected_choices = models.ManyToManyField(
        Choice,
        related_name='group_responses_selected',
        blank=True,
    )

    # Evaluation fields
    points_awarded = models.PositiveIntegerField(default=0)

    # Telemetry/extra data
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('attempt', 'question')]
        indexes = [
            models.Index(fields=["attempt", "question"]),
            models.Index(fields=["question", ]),
        ]
        verbose_name = 'Group Response'
        verbose_name_plural = 'Group Responses'

    def __str__(self):
        return f"GroupResponse({self.attempt_id}, Q={self.question_id})"


# Rankings
class UserRanking(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ranking')
    points = models.PositiveIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserRanking({self.user_id})"


class GroupRanking(models.Model):
    group = models.OneToOneField('TriviaGroup', on_delete=models.CASCADE, related_name='ranking')
    points = models.PositiveIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GroupRanking({self.group_id})"


def _bump_monthly_points(meta: dict, dt, delta_points: int):
    """Increment metadata bucket with top-level keys like {'YYYY-MM': points}."""
    try:
        month_key = dt.strftime('%Y-%m')
        current = int((meta or {}).get(month_key, 0))
        meta[month_key] = current + int(delta_points)
    except Exception:
        pass
    return meta


@receiver(post_save, sender='home.UserResponse')
def update_user_ranking_on_response(sender, instance, created, **kwargs):
    if not created:
        return
    # Only individual attempts should count toward user ranking
    try:
        ranking, _ = UserRanking.objects.get_or_create(user=instance.attempt.user)
    except Exception:
        return
    delta = int(instance.points_awarded or 0)
    ranking.points = int(ranking.points) + delta
    # Compute penalty from response metadata if present
    meta = instance.metadata or {}
    wrong = int(meta.get('wrong_selected', 0) or 0)
    qpen = int(meta.get('question_penalty', 0) or 0)
    ranking.penalty = int(ranking.penalty) + (wrong * qpen)
    ranking.metadata = _bump_monthly_points(ranking.metadata or {}, timezone.now(), delta)
    ranking.save(update_fields=['points', 'penalty', 'metadata', 'updated_at'])


@receiver(post_save, sender='home.GroupResponse')
def update_group_ranking_on_response(sender, instance, created, **kwargs):
    if not created:
        return
    # Group attempts count strictly toward group ranking only
    try:
        ranking, _ = GroupRanking.objects.get_or_create(group=instance.group)
    except Exception:
        return
    delta = int(instance.points_awarded or 0)
    ranking.points = int(ranking.points) + delta
    # Compute penalty from response metadata if present
    meta = instance.metadata or {}
    wrong = int(meta.get('wrong_selected', 0) or 0)
    qpen = int(meta.get('question_penalty', 0) or 0)
    ranking.penalty = int(ranking.penalty) + (wrong * qpen)
    ranking.metadata = _bump_monthly_points(ranking.metadata or {}, timezone.now(), delta)
    ranking.save(update_fields=['points', 'penalty', 'metadata', 'updated_at'])


class Challenge(TimeStampedModel):
    """
    Container for multi-participant challenges in strict mode:
    - mode='individual' (users only) OR mode='group' (groups only)
    Supports multiple rounds; winner is best-of N (majority of rounds).
    Standings are computed from linked attempts via ChallengeRoundAttempt.
    """
    MODE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    mode = models.CharField(max_length=12, choices=MODE_CHOICES)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    # If null, treat as single-round; if set, should be odd (e.g., 3, 5) for majority
    best_of = models.PositiveIntegerField(null=True, blank=True, help_text='Odd number of rounds for best-of; null for single-round')
    max_participants = models.PositiveIntegerField(default=2, help_text='Maximum number of participants allowed in this challenge')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_challenges')
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["mode", "status"]),
            models.Index(fields=["scheduled_at"]),
        ]

    def __str__(self):
        return f"Challenge({self.id}, {self.mode}, {self.status})"

    def clean(self):
        if self.expires_at and self.scheduled_at and self.expires_at < self.scheduled_at:
            raise ValidationError('expires_at must be after scheduled_at')
        if self.best_of is not None:
            if self.best_of <= 0:
                raise ValidationError('best_of must be a positive integer')
            if self.best_of % 2 == 0:
                raise ValidationError('best_of should be an odd number to ensure a clear majority')
        if self.max_participants is None or self.max_participants < 2:
            raise ValidationError('max_participants must be at least 2')


class ChallengeParticipant(TimeStampedModel):
    """
    Participant in a challenge. Exactly one of user or group must be set.
    All participants must match the challenge.mode.
    """
    ROLE_CHOICES = [
        ('challenger', 'Challenger'),
        ('invitee', 'Invitee'),
    ]
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='challenge_participations')
    group = models.ForeignKey('TriviaGroup', on_delete=models.CASCADE, null=True, blank=True, related_name='challenge_participations')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='invitee')
    is_active = models.BooleanField(default=True)
    team_name = models.CharField(max_length=100, blank=True)
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["challenge"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        who = self.user or self.group
        return f"Participant({who})"

    def clean(self):
        if bool(self.user) == bool(self.group):
            raise ValidationError('Exactly one of user or group must be set for a participant.')
        if self.challenge_id:
            if self.challenge.mode == 'individual' and not self.user:
                raise ValidationError('Challenge in individual mode requires user participants.')
            if self.challenge.mode == 'group' and not self.group:
                raise ValidationError('Challenge in group mode requires group participants.')


class ChallengeRound(TimeStampedModel):
    """
    A round in a challenge. Optionally specify the quiz for the round.
    """
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveIntegerField(default=1)
    quiz = models.ForeignKey('TestQuiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='challenge_rounds')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['round_number', 'id']
        constraints = [
            models.UniqueConstraint(fields=['challenge', 'round_number'], name='uniq_challenge_round_number')
        ]

    def __str__(self):
        return f"ChallengeRound({self.challenge_id}, #{self.round_number})"


class ChallengeRoundAttempt(TimeStampedModel):
    """
    Links existing attempts to a challenge participant (and round).
    Exactly one of user_attempt or group_attempt must be set matching the challenge mode.
    """
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='linked_attempts')
    round = models.ForeignKey(ChallengeRound, on_delete=models.CASCADE, null=True, blank=True, related_name='linked_attempts')
    participant = models.ForeignKey(ChallengeParticipant, on_delete=models.CASCADE, related_name='linked_attempts')
    user_attempt = models.ForeignKey('TestQuizAttempt', on_delete=models.CASCADE, null=True, blank=True, related_name='challenge_links')
    group_attempt = models.ForeignKey('GroupTestQuizAttempt', on_delete=models.CASCADE, null=True, blank=True, related_name='challenge_links')

    class Meta:
        indexes = [
            models.Index(fields=["challenge"]),
        ]
        constraints = [
            models.CheckConstraint(check=(
                (Q(user_attempt__isnull=False) & Q(group_attempt__isnull=True)) |
                (Q(user_attempt__isnull=True) & Q(group_attempt__isnull=False))
            ), name='chk_one_attempt_linked'),
        ]

    def clean(self):
        # Enforce strict mode consistency
        if self.participant_id and self.challenge_id:
            if self.challenge.mode == 'individual' and not self.user_attempt:
                raise models.ValidationError('Individual mode requires a user_attempt.')
            if self.challenge.mode == 'group' and not self.group_attempt:
                raise models.ValidationError('Group mode requires a group_attempt.')