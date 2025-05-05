def user_branch(request):
    """Add user branch information to all template contexts."""
    if request.user.is_authenticated:
        return {
            'user_branch': request.user.branch,
            'user_role': request.user.role
        }
    return {}