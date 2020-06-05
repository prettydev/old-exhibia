jQuery(document).ready(function($) {

    //button-top
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('#go-up').show();
        } else {
            $('#go-up').hide();
        }
    });

    $('#go-up').click(function () {
        $('.header').ScrollTo(0);
    });

    function display_form_errors(errors, captcha, $form) {
        if(captcha) {
            $('.captcha').closest('tr').empty().append(captcha);
        }
        for (var k in errors) {
            $form.find('label.error[for="id_' + k + '"]').append(errors[k]).show()
        }

    }

    $('body').on('click', '.ajax-submit', function () {
        var id = $(this).attr('id');
        var _this = $(this);
        var ajax_disable = $(this).data('ajax-disable');
        // дизейблим кнопку пока віполняется аjax
        if(ajax_disable) {
            $(this).addClass('disabled');
        }
        $(this).find('.loader').show();
        $('#' + id + '-form').ajaxSubmit({
            success: function (data, statusText, xhr, $form) {
                // Удаляем ошибки если были
                $form.find('.error').empty().hide();
                $(_this).find('.loader').hide();
                if (data['result'] == 'success') {
                    if (data.hasOwnProperty('next')) {
                        next = data['next'];
                        window.location.href = next;
                    }
                    else if (data.hasOwnProperty('callback_js')) {
                        eval(data['callback_js']);
                    }
                    else {
                        window.location.reload();
                    }
                }
                else if (data['result'] == 'error') {
                    // снова отображаем кнопку
                    $(_this).removeClass('disabled');
                    display_form_errors(data['response'], data['captcha'], $form);
                }
            },
            dataType: 'json'
        });
    });


  var chatArea = document.getElementById('chatMessages'); // element to make resizable

  if(chatArea){
    chatArea.className = chatArea.className + ' resizable';
    var resizer = document.getElementById('im_resizer_wrap');
    resizer.addEventListener('mousedown', initDrag, false);
  }

  var startX, startY, startWidth, startHeight;

  function initDrag(e) {
    startX = e.clientX;
    startY = e.clientY;
//    startWidth = parseInt(document.defaultView.getComputedStyle(chatArea).width, 10);
    startHeight = parseInt(document.defaultView.getComputedStyle(chatArea).height, 10);
    document.documentElement.addEventListener('mousemove', doDrag, false);
    document.documentElement.addEventListener('mouseup', stopDrag, false);
  }

  function doDrag(e) {
//    chatArea.style.width = (startWidth + e.clientX - startX) + 'px';
    var height = startHeight + e.clientY - startY;
    if (height >= 300) {
      chatArea.style.height = (height) + 'px';
    }
  }

  function stopDrag(e) {
    document.documentElement.removeEventListener('mousemove', doDrag, false);
    document.documentElement.removeEventListener('mouseup', stopDrag, false);
  }

  $('.prevCategory, .nextCategory').on('click', function(){
    var index = $('.item-tab .nav li.active').index();
    if (index || index == 0) {
      if ($(this).hasClass('prevCategory')) {
        index = index - 1;
      } else {
        index = index + 1;
      }


//        if (index-1 < 0) {
//          $('.prevCategory').addClass('noActive');
//        } else {
//          $('.prevCategory').removeClass('noActive');
//        }
//
//
//        if (index + 1 >= $('.item-tab .nav li').length) {
//          $('.nextCategory').addClass('noActive');
//        } else {
//          $('.nextCategory').removeClass('noActive');
//        }


      if (index >= 0) {
        $('.item-tab .nav li').eq(index).children().trigger('click');
      }

    }
    return false;
  });


});