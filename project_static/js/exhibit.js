function slotmachine(element, o, is_text_or_value) {
    var start_value = parseFloat(is_text_or_value ? element.text():element.val());
    $({someValue: start_value}).animate({someValue: o}, {
        duration: 1000,
        easing: 'swing',
        step: function () {
            if(is_text_or_value) {
                element.text(this.someValue.toFixed(0));
            } else {
                element.val(this.someValue.toFixed(0));
            }
        }
    });
}

/* display django flash messages with alertify */
function display_flash_message(message, type) {
    alertify.log(message, type.toLowerCase(), 0);
}

/* display django flash messages in profile area after social association */
function display_profile_message(message) {
    $('#profile_message').text(message);
    $('#profile_message').show();
    var seconds_left = 5;
    setInterval(function() {
        --seconds_left;
        if (seconds_left <= 0)
        {
            $('#profile_message').slideUp(400);
        }
    }, 1000);
}


/* change seconds left to format "HH:mm:ss" */
function view_time_left(time) {
    var hours = parseInt(time / 3600);
    var minutes_left = time % 3600;

    var minutes = parseInt(minutes_left / 60);
    var seconds = parseInt(minutes_left % 60);

    if(hours.toString().length == 1) {
        hours = '0'.concat(hours)
    }

    if(minutes.toString().length == 1) {
        minutes = '0'.concat(minutes)
    }


    if(seconds.toString().length == 1) {
        seconds = '0'.concat(seconds)
    }

    return [hours, minutes, seconds].join(':')
}

$(document).ready(function() {

    /* pretty price increasing in modal funding window */
    $('#fund-exhibit-form input[name="bids_cost"]').on('click', function(event){
        slotmachine($('#total-price'), $(this).val(), true);
    });

    /* user clicks bid button */
    $('body').on('click', '.bid-btn', function(event) {
        if($(this).hasClass('disabled')) {
            return false;
        }

        var exhibit_id = $(this).attr('data-exhibitid');
        var json_msg = {'type':'BID', 'exhibit_id': exhibit_id}
        ws.send(JSON.stringify(json_msg));
        return false;
    });

    /* profile item notifications window */
    $('body').on('click', '.addToWishList', function(event) {
        var item_pk = $(this).attr('data-itempk');
        $.ajax({
            type: "GET",
            url: "/profile/append-item-wishlist/",
            data: {'item_pk': item_pk },
            dataType: 'html',
            success: function (data) {
                if(data) {
                    $('#ModalWishList').html(data);
                }
                else {
                    $('#ModalSignIn').modal('show');
                }
            }
          });
    });

    /* initiate ajax call to get the right buy now form */
	$('body').on('click', '.btn-buy-now', function(event) {
        event.preventDefault();
        var item_pk = $(this).data('item_pk');
        var exists = $('#modal_buy_now_' + item_pk).length;
        if(!exists) {
            $.ajax({
                type: "GET",
                url: "/payment/append-buy-now-form/",
                data: {'item_pk': item_pk },
                dataType: 'html',
                success: function (data) {
                    if(data) {
                        $('#ModalBuyNow').html(data);
                        $('#ModalBuyNow').modal('show');
                    }
                    else {
                        $('#ModalSignIn').modal('show');
                    }

                }
            });
        } else {
            $('#ModalBuyNow').modal('show');
        }
    });

    /* setting exhibit_pk when modal funding window opens */
    $('body').on('click', '.fund', function() {
        $('#modal_funding_item').val($(this).attr('data-pk'));
    });

    $('.append_funding_carousel').click(function () {
        var category_id = $(this).data('id');
        var category_slug = $(this).data('slug');
        $('#' + category_slug).empty();
        $.ajax({
            type: "GET",
            url: "/exhibit/append-funding-carousel/",
            data: {'category_id': category_id },
            dataType: 'html',
            success: function (data) {
                if (data) {
                    $('#' + category_slug).html(data);
                }
            }
        });
    });


    /* admin timer drop tool */
    $('body').on('change', '.timer_drop_tool', function() {
        var exhibit_id = $(this).data('id');
        var new_time = $(this).val();

        $.ajax({
            type: "POST",
            url: "/exhibit/admin-timer-drop-tool/",
            data: {'exhibit_id': exhibit_id,
                   'new_time': new_time
            },
            dataType: 'html',
            success: function (data) {}
        });
    });

    $('body').on('click', '.check-coupon', function(event) {
        event.preventDefault();
        $(this).find('.loader').show();
        var coupon_code = $('#coupon_code').val();
        var _this = $(this);

        $.ajax({
            type: "POST",
            url: "/profile/check-coupon-code/",
            data: {'coupon_code': coupon_code},
            dataType: 'json',
            success: function (data) {
                $(_this).find('.loader').hide();
                if(data) {
                    if(data.result == 'success') {
                        $('#coupon_area').text(data.msg);
                        $('#coupon_error_msg').hide();
                        $('#coupon_code_hidden').val(coupon_code);
                    }
                    else {
                        $('#coupon_error_msg').text(data.msg).show();
                    }
                }
            }
        });
    });

/* append popup window data about user verification */
    $('.popover-wrapper-foto').popover({
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

    var chat_messages = $('.chat-messages');
    chat_messages.scrollTop(chat_messages.prop('scrollHeight'));

    /* show win limit if it exists */
    if(parseFloat($('#win_limit_counter').data('timeleft')) > 0) {
        $('#win_limit_panel').slideDown('300');
    }

    /* setting up win limit timer */
    var update_win_limit_timer = function() {
        var win_limit_counter = $('#win_limit_counter');
        var time_left = win_limit_counter.data('timeleft');
        if(parseInt(time_left) - 1 <= 0) {
            $('.bid-btn').removeClass('disabled');
            $('#win_limit_panel').slideUp('300');
        }
        win_limit_counter.data('timeleft', time_left - 1);
        win_limit_counter.text(view_time_left(time_left));
    }

    // todo start only if win limit exists
    setInterval(update_win_limit_timer, 1000);

    function update_bids_refund_timer() {
        $('.bidding-refund-timer').each(function() {
            var time_left = $(this).data('timeleft');
            if(parseInt(time_left) - 1 <= 0) {
                $(this).hide('500', function() { $(this).closest('table').remove() });
            }
            $(this).data('timeleft', time_left - 1);
            $(this).text(view_time_left(time_left));
//            win_limit_counter.text(view_time_left(time_left));
        })
    }

    // todo start only if exhibits with bids return exists
    setInterval(update_bids_refund_timer, 1000);

    /* append change password form */
    $('body').on('click', '#change-password', function(event) {

        if($('#ModalChangePassword').children().length == 0) {
            $.ajax({
                type: "GET",
                url: "/profile/change-password/",
                data: {},
                dataType: 'html',
                success: function (data) {
                    $('#ModalChangePassword').html(data);
                }
            });
        } else {
            $('#ModalChangePassword').modal('show');
        }
    });

    /* append change avatar form */
    $('body').on('click', '#change-avatar', function(event) {

        if($('#ModalChangeAvatar').children().length == 0) {
            $.ajax({
                type: "GET",
                url: "/profile/change-avatar/",
                data: {},
                dataType: 'html',
                success: function (data) {
                    $('#ModalChangeAvatar').html(data);
                }
            });
        } else {
            $('#ModalChangeAvatar').modal('show');
        }
    });

    /* append modal phone and email verification forms */
    $('body').on('click', '#verify-phone, #verify-email', function(event) {

        $('#ModalVerify').empty();
        var action_url = $(this).data('action-url');

        $.ajax({
            type: "GET",
            url: action_url,
            data: {},
            dataType: 'html',
            success: function (data) {
                $('#ModalVerify').html(data);
            }
        });

    });

    /* remove user avatar */
    $('body').on('click', '#remove-user-avatar', function(event) {

        $.ajax({
            type: "POST",
            dataType: 'json',
            url: '/profile/remove-user-avatar/',
            success: function (data) {
                // set default image if it where deleted
                $('#user-avatar').attr('src', defaultImagePath);
            }
        });

    });


    /* initiate ajax call to get the right buy shipping form */
	$('body').on('click', '.btn-buy-shipping', function(event) {
        event.preventDefault();
        var exhibit_id = $(this).data('exhibit_id');
        var exists = $('#modal_shipping_now_' + exhibit_id).length;
        if(!exists) {
            $.ajax({
                type: "GET",
                url: "/payment/append-buy-shipping-form/",
                data: {'exhibit_id': exhibit_id },
                dataType: 'html',
                success: function (data) {
                    if(data) {
                        $('#ModalBuyShipping').html(data);
                        $('#ModalBuyShipping').modal('show');
                    }
                }
            });
        } else {
            $('#ModalBuyShipping').modal('show');
        }
    });


    /* initiate ajax call to get the right buy item with bids return form */
	$('body').on('click', '.btn-return-bids', function(event) {
        event.preventDefault();
        var exhibit_id = $(this).data('exhibit_id');
        var exists = $('#modal_return_bids_' + exhibit_id).length;
        if(!exists) {
            $.ajax({
                type: "GET",
                url: "/payment/append-bids-return-form/",
                data: {'exhibit_id': exhibit_id },
                dataType: 'html',
                success: function (data) {
                    if(data) {
                        $('#ModalReturnBids').html(data);
                        $('#ModalReturnBids').modal('show');
                    }
                }
            });
        } else {
            $('#ModalReturnBids').modal('show');
        }
    });




    /* get modal item page */
    $('body').on('click', '.append-item-page', function(event) {
        event.preventDefault();
        var item_pk = $(this).data('pk');
        var exists = $('#item_modal_' + item_pk).length;
        if(!exists){
            $.ajax({
                type: "GET",
                url: "/exhibit/append_item_page/",
                data: {'item_pk': item_pk },
                dataType: 'html',
                success: function (data) {
                    if(data) {
                        $('#ModalItemPage').html(data);
                        $('#ModalItemPage').modal('show');
                    }
                }
            });
        }else{
            $('#ModalItemPage').modal('show');
        }
    });

    /* delete not payed orders */
    $('body').on('click', '.btn-cancel-order', function(event) {
        event.preventDefault();
        var _this = $(this);
        alertify.confirm('confirm delete?', function (e) {
            if (e) {
                var transaction_id = $(_this).data('pk');
                console.log(transaction_id);
                $.ajax({
                    type: "POST",
                    url: "/payment/cancel-order/",
                    data: {'transaction_id': transaction_id },
                    dataType: 'json',
                    success: function (data) {
                        if(data && data.result == "success") {
                            window.location.href = data.next;
                        }
                        else {
                          alertify.alert("Can't delete this order");
                        }
                    }
                });
            }
        });
    });

    /* pause/unpause all exhibits */
    $('body').on('click', '.pause-all-exhibits', function(event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: $(this).data('action-url'),
            dataType: 'json',
            success: function (data) {
                if(data && data.result == "success") {
                    alertify.alert("Exhibits state was successfuly updated");
                }
                else {
                    alertify.alert("An error occured");
                }
            }
        });
    });

    /* toogle funding modal views (standart/funding credits) */
    $('body').on('change', '#use_funding_credits', function(event) {
        event.preventDefault();
        if($(this).prop('checked')) {
            $('.buy-bids-area').slideUp(400, function() { $('.funding-credits-area').slideDown(400); });
            var button_text = $('#button-text');
            $(button_text).text(button_text.data('bonus-text'));
        }
        else {
            $('.funding-credits-area').slideUp(400, function() { $('.buy-bids-area').slideDown(400); });
            var button_text = $('#button-text');
            $(button_text).text(button_text.data('standart-text'));
        }
    });

    /* disable/enable guest chat */
    $('body').on('click', '#toogle-guest-chat', function() {
        var $el = $(this);
        var status = $el.data('chat-status');
        var text = status ? 'disable' : 'enable';

        if(!confirm('Are you sure to ' + text + ' guest chat?')){
            return;
        }

        $.ajax({
            type: "POST",
            url: $(this).data('action-url'),
            data: {'status': status},
            dataType: 'json',
            success: function (data) {
                var text;
                if(data && data.result == "success") {
                    alertify.alert("Guest chat state was successfuly updated");
                    $el.toggleClass('btn-danger');
                    $el.toggleClass('btn-success');

                    if(status === 1) {
                        text = $el.data('enable-message');    
                    }
                    else {
                        text = $el.data('disable-message');    
                    }

                    $el.text(text);
                    $el.data('chat-status', 1 - status);
                }
                else {
                    alertify.alert("An error occured");
                }
            }
        });
    });
    

});

