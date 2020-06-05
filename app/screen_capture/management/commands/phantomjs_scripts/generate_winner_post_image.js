var page = require('webpage').create(),
    system = require('system'),
    exhibia_url = 'http://127.0.0.1:8000',
    images_path = '/var/www/exhibia/media/winner_posts/',
    args;
        
args = system.args;

if(args.length === 1){
    console.log('Exhibit id must be provided as argument!');
    phantom.exit();
}

exhibit_id = args[1];

page.open(exhibia_url, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
    } else {
        window.setTimeout(function () {      
            try {
                var bb = page.evaluate(function (exhibit_id) { 
                    var exhibit_box = document.getElementById("bidding_" + exhibit_id);
                    if(!exhibit_box) {
                        console.log('Can not find exhibit html box!');
                    }
                    return exhibit_box.getBoundingClientRect(); 
                },  exhibit_id);

                page.clipRect = {
                    top:    bb.top-1,
                    left:   bb.left-1,
                    bottom: bb.bottom+1,
                    right:  bb.right+1,
                    width:  bb.width,
                    height: bb.height
                }
                page.render(images_path + exhibit_id + '_exhibit_winner.png');
            } finally {
                phantom.exit();
                console.log( exhibit_id + '_exhibit_winner.png');
            }
        }, 200);
    }
});
