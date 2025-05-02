# context processors are used to check if the user has unread notifications for every user request in the system.
def unread_notifications(request):
    if request.user.is_authenticated:
        return {'has_unread_notifications': request.user.notifications.filter(is_read=False).exists()}
    return {'has_unread_notifications': False}