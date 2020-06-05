exhibia =
  renderEmoticons: (message) ->
    emoticonUrl = '/static/img/emoticons/'
    textToEmoticon =
      ":'(": 'Crying.png',
      ":''(": 'Crying2.png',
      ">:)": 'Devil.png',
      ':P~': 'Drooling.png',
      "<3": 'Heart.png',
      ':X': 'Not-Talking.png',
      'O:)': 'Sacred.png',
      ':)': 'smile.png',
      ':(': 'Sad.png',
      ':|': 'Straight-Face.png',
      ':P': 'Tongue.png',
      ';)': 'Winking.png',
      ':D': 'Big-Grin.png',
      '_b': 'Cool.png'


    if typeof(message) is 'string' # With new strings
      for emoticon, image of textToEmoticon
        message = message.replace(emoticon, "<img src='#{emoticonUrl}#{textToEmoticon[emoticon]}' alt='#{image}'/>")
      return message
    else
      throw "Message string not provided"

$(document).ready ->
  # Render initial commits
  for comment in $('div.comment')
    $(comment).html(exhibia.renderEmoticons($(comment).html()))

  # GET to tracking cookie
  if typeof location.hash != 'undefined' and location.hash == '#_-_'
    $.get('/exhibit/tracking-code/', service_provider: 'facebook', (data) ->
      $(data).find('script:first').appendTo('body')
    )

