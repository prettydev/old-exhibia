/* jQuery fineUploader settings for user avatar */
var avatarFineUploaderSettings = {
        request: {
            endpoint: '/profile/upload-avatar/',
            forceMultipart: false
        },
        multiple: false,
        debug: true,
        validation: {
            allowedExtensions: ['jpeg', 'jpg', 'gif', 'png'],
            itemLimit: 20
        },
        dragAndDrop: {
            disableDefaultDropzone: true
        },
        deleteFile: {
            enabled: true,
            forceConfirm: false,
            endpoint: '/profile/remove-avatar-from-temp'
        },
        callbacks: {
            onDelete: function (id) {
                this.setDeleteFileParams({filename: this.getName(id)}, id);
            }
        },
        template: "qq-avatar-template"
    };

var defaultImagePath = '/static/img/user-no-image.jpg';
var deleteButton = $('<a class="qq-upload-delete-selector qq-upload-delete" href="javascript:void(0);">Delete</a>');