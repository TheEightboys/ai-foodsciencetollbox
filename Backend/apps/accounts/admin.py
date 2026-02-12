from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import User, TeacherProfile, UserPreferences


# Import at module level to avoid circular imports
try:
    from apps.memberships.models import UserMembership
    
    class UserMembershipInline(admin.StackedInline):
        """Inline admin for UserMembership"""
        model = UserMembership
        extra = 0
        can_delete = False
        fields = ('tier', 'status', 'generations_used_this_month', 'current_period_start', 'current_period_end', 'admin_override_unlimited')
        readonly_fields = ('generations_used_this_month',)
        
        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.select_related('tier')
except ImportError:
    # If memberships app is not available, create a dummy inline
    UserMembershipInline = None


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Enhanced User Admin for superadmin"""
    list_display = ('email', 'full_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'membership_status')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [UserMembershipInline] if UserMembershipInline else []
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Superuser has all permissions automatically'
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or '—'
    full_name.short_description = 'Name'
    
    def membership_status(self, obj):
        """Display membership status"""
        try:
            membership = obj.membership
            status_colors = {
                'active': 'green',
                'past_due': 'orange',
                'canceled': 'red',
                'trialing': 'blue'
            }
            color = status_colors.get(membership.status, 'black')
            return format_html(
                '<span style="color: {};">{} - {}</span>',
                color,
                membership.tier.display_name,
                membership.status
            )
        except:
            return format_html('<span style="color: gray;">No membership</span>')
    membership_status.short_description = 'Membership'
    
    def save_model(self, request, obj, form, change):
        """Override save to create membership if user is new"""
        super().save_model(request, obj, form, change)
        
        # If user is newly created, ensure they have a membership
        if not change:  # New user
            from apps.memberships.models import MembershipTier, UserMembership
            try:
                # Check if membership already exists (from signals)
                if not hasattr(obj, 'membership'):
                    # Get trial tier or first active tier
                    tier = MembershipTier.objects.filter(name='trial').first()
                    if not tier:
                        tier = MembershipTier.objects.filter(is_active=True).first()
                    
                    if tier:
                        UserMembership.objects.create(
                            user=obj,
                            tier=tier,
                            status='trialing' if tier.name == 'trial' else 'active',
                            current_period_start=timezone.now().date(),
                            current_period_end=(timezone.now() + timedelta(days=7)).date() if tier.name == 'trial' else (timezone.now() + timedelta(days=30)).date()
                        )
            except Exception as e:
                # Don't fail user creation if membership creation fails
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to create membership for user {obj.email}: {e}")
    
    actions = ['assign_trial', 'assign_starter', 'assign_pro']
    
    def assign_trial(self, request, queryset):
        """Assign trial membership to selected users"""
        from apps.memberships.models import MembershipTier, UserMembership
        tier = MembershipTier.objects.filter(name='trial').first()
        if not tier:
            self.message_user(request, 'Trial tier not found. Please create it first.', level='error')
            return
        
        count = 0
        for user in queryset:
            membership, created = UserMembership.objects.get_or_create(
                user=user,
                defaults={
                    'tier': tier,
                    'status': 'trialing',
                    'current_period_start': timezone.now().date(),
                    'current_period_end': (timezone.now() + timedelta(days=7)).date()
                }
            )
            if not created:
                membership.tier = tier
                membership.status = 'trialing'
                membership.current_period_end = (timezone.now() + timedelta(days=7)).date()
                membership.save()
            count += 1
        self.message_user(request, f'Assigned Trial membership to {count} user(s).')
    assign_trial.short_description = 'Assign Trial membership'
    
    def assign_starter(self, request, queryset):
        """Assign starter membership to selected users"""
        from apps.memberships.models import MembershipTier, UserMembership
        tier = MembershipTier.objects.filter(name='starter').first()
        if not tier:
            self.message_user(request, 'Starter tier not found. Please create it first.', level='error')
            return
        
        count = 0
        for user in queryset:
            membership, created = UserMembership.objects.get_or_create(
                user=user,
                defaults={
                    'tier': tier,
                    'status': 'active',
                    'current_period_start': timezone.now().date(),
                    'current_period_end': (timezone.now() + timedelta(days=30)).date()
                }
            )
            if not created:
                membership.tier = tier
                membership.status = 'active'
                membership.current_period_end = (timezone.now() + timedelta(days=30)).date()
                membership.save()
            count += 1
        self.message_user(request, f'Assigned Starter membership to {count} user(s).')
    assign_starter.short_description = 'Assign Starter membership'
    
    def assign_pro(self, request, queryset):
        """Assign pro membership to selected users"""
        from apps.memberships.models import MembershipTier, UserMembership
        tier = MembershipTier.objects.filter(name='pro').first()
        if not tier:
            self.message_user(request, 'Pro tier not found. Please create it first.', level='error')
            return
        
        count = 0
        for user in queryset:
            membership, created = UserMembership.objects.get_or_create(
                user=user,
                defaults={
                    'tier': tier,
                    'status': 'active',
                    'current_period_start': timezone.now().date(),
                    'current_period_end': (timezone.now() + timedelta(days=30)).date()  # Monthly for Pro
                }
            )
            if not created:
                membership.tier = tier
                membership.status = 'active'
                membership.current_period_start = timezone.now().date()
                membership.current_period_end = (timezone.now() + timedelta(days=30)).date()  # Monthly for Pro
                membership.save()
            count += 1
        self.message_user(request, f'Assigned Pro membership to {count} user(s).')
    assign_pro.short_description = 'Assign Pro membership'


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin interface for Teacher Profiles"""
    list_display = ('user_email', 'is_academy_member', 'email_verified', 'terms_accepted', 'created_at')
    list_filter = ('is_academy_member', 'email_verified', 'terms_accepted', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'verification_info')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Academy Membership', {
            'fields': ('is_academy_member',)
        }),
        ('Email Verification', {
            'fields': ('email_verified', 'verification_info', 'email_verification_token', 'email_verification_sent_at')
        }),
        ('Password Reset', {
            'fields': ('password_reset_token', 'password_reset_expires'),
            'classes': ('collapse',)
        }),
        ('Legal', {
            'fields': ('terms_accepted', 'terms_accepted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def verification_info(self, obj):
        """Display verification status"""
        if obj.email_verified:
            return format_html('<span style="color: green; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: red;">✗ Not Verified</span>')
    verification_info.short_description = 'Status'
    
    actions = ['verify_emails', 'send_verification_emails']
    
    def verify_emails(self, request, queryset):
        """Admin action to manually verify emails"""
        count = 0
        for profile in queryset:
            if not profile.email_verified:
                profile.verify_email()
                count += 1
        self.message_user(request, f'Verified {count} email(s).')
    verify_emails.short_description = 'Verify selected emails'


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for User Preferences"""
    list_display = ('user_email', 'preferred_grade_level', 'preferred_subject', 'preferred_tone', 'default_question_count', 'updated_at')
    list_filter = ('preferred_grade_level', 'preferred_subject', 'preferred_tone', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('updated_at',)
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'