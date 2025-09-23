from django import template

register = template.Library()

@register.filter
def display_name(user):
    """Return the best display name for a user.
    - If PersonalProfile exists and has any name parts, use them.
    - Else, return the email without the domain part.
    - Fallback to full email if needed.
    """
    try:
        profile = getattr(user, 'profile', None)
        if profile:
            # Prefer first + last, else surname, else any available
            parts = [p for p in [profile.first_name, profile.last_name] if p]
            if parts:
                return " ".join(parts)
            if profile.surname:
                return profile.surname
    except Exception:
        pass

    # Fallback to email local-part
    email = getattr(user, 'email', '') or ''
    if '@' in email:
        return email.split('@', 1)[0]
    # Last resort
    return email or 'User'
