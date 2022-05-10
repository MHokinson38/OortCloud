//==============================
// File Submission JS 
//==============================
const fileUploadForm = document.getElementById('fileUploadForm');
const submitButton = document.getElementById('uploadSubmitButton');
const fileInput =  document.getElementById('id_upload');

// The janky way to check if we are on submission page, move this to js which only runs there
const progressBox = document.getElementById('progressBox');
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0];  // Should only have a single token 
console.log(csrf);

// File submit event listener 
submitButton.addEventListener('click', () => {
    console.log('triggered upload event');
    progressBox.classList.remove('not-visible');

    // Gather the form data to put information into the progress bar 
    const fd = new FormData();
    const file_data = fileInput.files[0]; // Only uploading a single file at a time, this is fine 
    fd.append('csrfmiddlewaretoken', csrf.value);
    fd.append('file', file_data);

    console.log(file_data);

    $.ajax({
        type: 'POST',
        url: fileUploadForm.action,
        enctype: 'multipart/form-data',
        data: fd,
        beforeSend: function() {

        },
        // This event update is giving us the amount of the file which we have loaded so far 
        // Basically the main crux of the progress bar 
        xhr: function() { 
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', e => {
                console.log(e);
                if (e.lengthComputable) {
                    const percent = e.loaded / e.total * 100;
                    console.log(percent);
                }
            });

            return xhr;
        },
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        },
        cache: false, 
        contentType: false,
        processData: false,
    });
});

