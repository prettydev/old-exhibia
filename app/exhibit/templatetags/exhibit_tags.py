from django import template
register = template.Library()

@register.inclusion_tag('exhibit/bid_button.html',  takes_context=True)
def bid_button(context, exhibit):
    """
    In this template tag we should decide should we add bid button or not
    """
    user = context['user']
    params = {'exhibit_id': exhibit.id, 'bid_allowed': False, 'ended': False}
    if exhibit.in_after_win_pause or exhibit.in_auto_paused_last or exhibit.is_relisted:
        params['ended'] = True
    else:
        if user.is_authenticated():
            if not user.is_on_win_limit(giveaway=exhibit.item.giveaway):
                if exhibit.item.newbie:
                    if user.is_newbie:
                        params['bid_allowed'] = True
                    else:
                        params['newbie'] = True
                elif exhibit.locked:
                    if exhibit.is_locked_by(user):
                        params['bid_allowed'] = True
                    else:
                        params['locked'] = True
                else:
                    params['bid_allowed'] = True
        else:
            params['not_logged'] = True

    return params