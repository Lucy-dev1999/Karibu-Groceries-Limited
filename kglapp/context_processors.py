def user_branch(request):
    """Add user branch information to all template contexts."""
    if request.user.is_authenticated:
        # Determine the current branch from URL parameter or user's branch
        current_branch = request.GET.get('branch', request.user.branch)
        
        # Define color palettes for each branch
        if current_branch == 'Mattuga':
            branch_colors = {
                'primary': '#00A859',      # Green
                'secondary': '#00C96B',    # Lighter green
                'accent': '#B3E5D1',       # Mint green
            }
        elif current_branch == 'Maganjo':
            branch_colors = {
                'primary': '#0066CC',      # Blue
                'secondary': '#3399FF',    # Lighter blue
                'accent': '#B3D9FF',       # Light blue
            }
        else:
            # Default colors
            branch_colors = {
                'primary': '#00A859',
                'secondary': '#00C96B',
                'accent': '#B3E5D1',
            }
        
        return {
            'user_branch': request.user.branch,
            'user_role': request.user.role,
            'current_branch': current_branch,
            'branch_colors': branch_colors
        }
    return {}