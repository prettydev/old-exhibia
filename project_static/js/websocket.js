/*check if user's browser support WebSocket protocol */
if ("WebSocket" in window) {
    /* connect to Tornado WebSocket */
    var ws = new WebSocket(window.WEBSOCKET_ADDRESS);

    ws.onopen = function(event) {
        // send bidding displaying type to store it in WebSockets server side
        var json_msg = {'type':'INIT', 'mobile_version': window.MOBILE_VERSION}
        ws.send(JSON.stringify(json_msg));
    }

    /* message handler from WebScoket */
    ws.onmessage = function (event) {
        var data = JSON.parse(event.data);

        MESSAGE_CALLBACKS[data.type](data);
        // if there was some system notification, add id to chat area
        if(data.hasOwnProperty('sys_notifications')) {
            var chat_messages = $('#chatMessages');
            for(key in data.sys_notifications) {
                var msg =
                    '<li>' +
                        '<div>' +
                            '<i class="icon-attention"></i>' +
                            '<span>' + data.sys_notifications[key] +'</span>' +
                        '</div>' +
                    '</li>';

                $(chat_messages).append(msg);
            }
            $(chat_messages).scrollTop(chat_messages.prop('scrollHeight'));
        }
    }

    /* error handler */
    ws.onerror = function (event) {
        console.log('error!');
    }

    /* websocket server close connection */
    ws.onclose = function(event) {
        // stop timers and show error
        $('.bidding-timer').removeClass('time');
        $('.bidding-timer').addClass('color-blue');
        $('.bidding-timer').text('-- : --');
        $('.start-message').text('-- : --');
    }
} else {
    alertify.alert('Your browser doesn\'t support websockets. Please update it');
}

/* all callback functions for messages from server */
var MESSAGE_CALLBACKS = {
    'CHAT_MESSAGE': on_chat_message,
    'CHAT_BANNED': on_chat_banned,
    'CANNOT_BID': on_cannot_bid,
    'SUCCESS_BID': on_success_bid,
    'WON_EXHIBIT': on_won_exhibit,
    'UPDATE_PROFILE': on_update_profile,
    'UPDATE_USER_COUNTER': on_active_users_counter_update,
    'UPDATE_ACTIVE_EXHIBITS': on_update_active_exhibits,
    'UPDATE_PAUSED_EXHIBITS' : on_update_paused_exhibits,
    'ADD_NEW_BIDDINGS': on_add_new_exhibits,
    'UPDATE_FUNDING_EXHIBIT': on_update_funding_exhibit,
    'EXHIBIT_TIMER_DROPPED': on_exhibit_timer_dropped,
    'RELIST_EXHIBITS': on_relist_exhibits
}

/* main function. that updates all active exhibits in status "bidding" */
function on_update_active_exhibits(data) {
    for(var key in data.data) {
        var exhibit = data.data[key];

        $('#bidding_wrapper_foto_' + exhibit.id).show();

        var bidder_img = $('#bidding_foto_' + exhibit.id).attr('src');

        if(bidder_img != exhibit.bidder_img) {
            $('#bidding_wrapper_foto_' + exhibit.id).data('content', '');
            $('#bidding_wrapper_foto_' + exhibit.id).data('user-id', exhibit.bidder_id);
            $('#bidding_foto_' + exhibit.id).attr('src', exhibit.bidder_img);
            $('#bidding_foto_' + exhibit.id).rotate3Di(
                '360',
                1000
            );
        }

        $('#bidding_name_' + exhibit.id).text(exhibit.bidder_name);

        // check if exhibit ends
        if(exhibit.hasOwnProperty('end')) {
            $('#bidding_timer_' + exhibit.id).remove();
            $('#bidding_button_' + exhibit.id).remove();
            $('#bidding_winner_' + exhibit.id).show('500');
        }
        else if(exhibit.hasOwnProperty('pause_all')) {
            $('#bidding_start_msg_' + exhibit.id).remove();
            $('#bidding_timer_' + exhibit.id).text('paused').show();
        }
        else if(exhibit.hasOwnProperty('paused')) {
            $('#bidding_start_msg_' + exhibit.id).remove();
            $('#bidding_timer_' + exhibit.id).text('resetting').show();
        }
        else if(exhibit.hasOwnProperty('auto_paused')) {
            $('#bidding_start_msg_' + exhibit.id).remove();
            $('#bidding_timer_' + exhibit.id).text('Going').show();
        }
        else if(exhibit.hasOwnProperty('auto_paused_last')) {
            $('#bidding_start_msg_' + exhibit.id).remove();
            $('#bidding_button_' + exhibit.id).remove();
            $('#bidding_timer_' + exhibit.id).text('Gone').show(500);
        }
        // update timer
        else {
            $('#bidding_start_msg_' + exhibit.id).remove();
            $('#bidding_timer_' + exhibit.id).text(exhibit.time_left).show();
            // check if exhibit is locked
            if(exhibit.hasOwnProperty('locked_by')) {
                if(exhibit.user.id && exhibit.locked_by.indexOf(exhibit.user.id) === -1) {
                    // disable user from this bidding
                    $('#bidding_button_' + exhibit.id).remove();
                    $('#bidding_locked_message_' + exhibit.id).show();
                }
            }
        }
    }
}

/* admin drop timer for exhibit */
function on_exhibit_timer_dropped(data) {
    $('#bidding_' + data['exhibit_id']).find('.item-timer span').text(data['new_time']);

}

/* relist exhibits */
function on_relist_exhibits(data) {
    for(var key in data.data) {
        var exhibit = data.data[key];
        $('#bidding_timer_' + exhibit.id).remove();
        $('#bidding_wrapper_foto_' + exhibit.id).hide();
        $('#bidding_name_' + exhibit.id).text('');
        $('#bidding_winner_' + exhibit.id).text('Relisted').show('500');
    }
}

/* updates user profile and bidding item after he made a bid */
function on_success_bid(data) {
    $('#bidding_wrapper_foto_' + data.id).show();

    var bidder_img = $('#bidding_foto_' + data.id).attr('src');

    if(bidder_img != data.bidder_img) {
            $('#bidding_wrapper_foto_' + data.id).data('user-id', data.bidder_id);
            $('#bidding_wrapper_foto_' + data.id).data('content', '');
            $('#bidding_foto_' + data.id).attr('src', data.bidder_img);
            $('#bidding_foto_' + data.id).rotate3Di(
                '360',
                1000
            );
        }

    $('#bidding_name_' + data.id).text(data.bidder_name);
    $('#profile_bids').text(data.bids);
    $('#profile_bonus_bids').text(data.bonus_bids);
    $('#profile_points').text(data.points);
}

/* updates profile info */
function on_update_profile(data) {
    $('#profile_bids').text(data.bids);
    $('#profile_bonus_bids').text(data.bonus_bids);
    $('#profile_points').text(data.points);
    $('#profile_wins').text(data.wins);
}

/* chat message from server handler */
function on_chat_message(data) {

    var message = $('<div class="comment"></div>').text(data.message).html();
    message = exhibia.renderEmoticons(message);

    var chat_msg =
        '<li>' +
          '<div class="foto">' +
              '<img src="' + data.avatar + '"/>' +
          '</div>' +
          '<div class="description">' +
            '<div class="user-description-box author" >' +
                '<a href="#" data-user-id="' + data.user_id + '" data-trigger="hover" data-container="body"' +
                'data-toggle="popover" data-html="true" data-placement="right" data-content="" class="popover-wrapper-foto ">' + data.username + '</a>' +
            '</div>' +
            '<div class="comment">' + message + '</div>' +
          '</div>' +
        '<div class="clearfix"></div>' +
        '</li>';

    var chat_messages = $('#chatMessages');
    
    chat_messages.append(chat_msg);
    chat_messages.scrollTop(chat_messages.prop('scrollHeight'));

    $('.popover-wrapper-foto:last').popover({
        html: true,
        trigger: 'manual',
        content: function() {
            var user_id = $(this).data('user-id');
            var content = $(this).data('content');

            if(content.length) {
                return content;
            }
            else {
                var response = $.ajax(
                {
                    url: "/profile/append-verification-popup/",
                    data: {'user_id': user_id },
                    dataType: 'html',
                    async: false
                }).responseText;

                $(this).data('content', response);

                return response;
            }
        }
      }).mouseenter(function(e) {
        $(this).popover('show');
      }).mouseleave(function(e) {
        $(this).popover('hide');
      });
}

/* insert new exhibits in "bidding" status */
function on_add_new_exhibits(data) {
    for(var key in data.data) {
        var exhibit = data.data[key],
            last_exhibit_before_giveaway;

        // insert new bidd (it can be already appeared if user press f5 in that moment)
        if($('#bidding_' + exhibit.id).length == 0) {
            // giveaways must be situated at 4,5 exhibit places (at first raw end)
            if(exhibit.giveaway) {
                last_exhibit_before_giveaway = $('#bidding_exhibits > div:eq(2)');
                if(last_exhibit_before_giveaway.length) {
                    $('#bidding_' + exhibit.id).hide('500', function() { $(this).remove() });
                    $(exhibit.bidding_box).insertAfter(last_exhibit_before_giveaway).show('500');
                    continue;
                }
            }

            $('#bidding_' + exhibit.id).hide('500', function() { $(this).remove() });
            $(exhibit.bidding_box).insertBefore('#last_bidding').show('500');
        }
    }
}

/* display user that he was banned */
function on_chat_banned(data) {
    alertify.alert(data.message);
}

/* remove exhibits with statuses 'full_fund_pause' and 'after_win_pause' (their view time have passed), 
    append new funding exhibits  
*/
function on_update_paused_exhibits(data) {
    // remove paused exhibits
    for(var key in data.removed) {
        var exhibit = data.removed[key],
            exhibit_box,
            box_position,
            last_bidding_box,
            cloned_last_bidding_box;

        exhibit_box = $('#' + exhibit.from_status + '_' + exhibit.id);

        if(exhibit.from_status == 'bidding') {

            box_position = exhibit_box.index('#bidding_exhibits > div');

            if (box_position < 3) {

                last_bidding_box = $('#last_bidding').prev();
                // todo add attribute 'giveaway' to exhibits boxes (don't forget about prototype templates) 
                if(last_bidding_box.attr('id') != exhibit_box.attr('id')){ 
                    last_bidding_box.hide('500', function() { 
                        cloned_last_bidding_box = $(this).clone().hide();
                        cloned_last_bidding_box.insertBefore(exhibit_box).show('500');
                        $(this).remove();
                    });    
                }
            }
            
            exhibit_box.hide('500', function() { $(this).remove() });    
        }
        else {
        // todo delete it using ("#owl-demo").data('owlCarousel').removeItem('targetPosition');
            exhibit_box.hide('500', function() { $(this).remove() });
        }

    }
    // append new
    for(var key in data.created) {
        var exhibit = data.created[key];
        for(key in exhibit.categories) {
            var owl = $('#owl-category-' + exhibit.categories[key]);
            if(owl.length != 0) {
                owl.data('owlCarousel').addItem(exhibit.funding_box);
                $('#funding_' + exhibit.id).show('500');
            }
        }
    }
}

/* update active users counter */
function on_active_users_counter_update(data) {
    $('#active-users-counter').text(data.count);
}

/* show message if user can't make a bid for some reasons (not enough credits, etc. ) */
function on_cannot_bid(data) {
    if(data.hasOwnProperty('nonauthorized')) {
        alertify.confirm(data.message, function (e) {
            if (e) {
                $('#ModalSignIn').modal('show');
            }
        });
    }
    else {
        alertify.alert(data.message);
    }
}

/* update funding progress for exhibit */
function on_update_funding_exhibit(data) {
    var exhibit_div = $('#funding_' + data.id)
    exhibit_div.find('.start-message').remove();
    exhibit_div.find('.backers-text-message').show();
    exhibit_div.find('.percent').show();
    exhibit_div.find('.bakers').text(data.backers);

    exhibit_div.find('.progress-bar').attr('style', 'width: ' + data.percent_funded + '%;');

    slotmachine(exhibit_div.find('.funded'), data.percent_funded, true);
}

/* update profile panel when user won exhibit */
function on_won_exhibit(data) {
    // update wins number
    $('#profile_wins').text(data.wins_number);
    console.log(data.is_on_win_limit);
    if(data.is_on_win_limit) {
        // show win limit box and start win limit timer
        $('#win_limit_counter').data('timeleft', data.win_limit_time_left);
        $('.bid-btn').addClass('disabled');
        $('#win_limit_panel').slideDown('300');
    }
}

$(document).ready(function() {
    /* user send chat message */
    $('#chat-msg').keyup(function(e) {

//        if (this.scrollHeight > this.offsetHeight) {
//            while (this.scrollHeight > this.offsetHeight) {
//                this.value = this.value.substr(0, this.value.length - 1);
//             }
//        }

        var code = e.which;
        var text = $.trim($(this).val());

        if(code==13 && text) {
            var json_msg = {'type':'CHAT_MESSAGE', 'message': text}
            ws.send(JSON.stringify(json_msg));
            $(this).val('');
        }
    });

});

