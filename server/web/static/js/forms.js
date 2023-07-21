(function () {
    "use strict";
  
    let forms = document.querySelectorAll('.login-form, ' + 
                                          '.register-form, ' + 
                                          '.edit-account-form, ' + 
                                          '.upload-recordings-form');
  
    forms.forEach( function(e) {
      e.addEventListener('submit', function(event) {
        event.preventDefault();
  
        let thisForm = this;
  
        let action = thisForm.getAttribute('action');
        
        if( ! action ) {
          displayError(thisForm, 'The form action property is not set!');
          return;
        }
        thisForm.querySelector('.loading').classList.add('d-block');
        thisForm.querySelector('.error-message').classList.remove('d-block');
  
        let formData = new FormData( thisForm );
        form_submit(thisForm, action, formData);
      });

      thisForm.querySelector('.input-file').addEventListener('change', function(event) {
        files_name = []
        for (file in event.target.files)
          files_name.push(file.name)
        
        event.target.previousSibling.innerHTML = files_name.join(', ')
      });
    });
  
    function form_submit(thisForm, action, formData) {
      fetch(action, {
        method: 'POST',
        body: formData,
        headers: {'X-Requested-With': 'XMLHttpRequest'}
      })
      .then(response => {
        if( response.ok ) {
          return response.text();
        } else {
          throw new Error(`${response.status} ${response.statusText} ${response.url}`); 
        }
      })
      .then(data => {
        thisForm.querySelector('.loading').classList.remove('d-block');
        if (data.trim() == 'OK') {
          successMessage = thisForm.querySelector('.success-message')
          if (successMessage == null)
            location.href = '';
          else {
            successMessage.classList.add('d-block');
            thisForm.reset();
          }
        } else {
          throw new Error(data ? data : 'Form submission failed and no error message returned from: ' + action); 
        }
      })
      .catch((error) => {
        displayError(thisForm, error);
      });
    }
  
    function displayError(thisForm, error) {
      thisForm.querySelector('.loading').classList.remove('d-block');
      thisForm.querySelector('.error-message').innerHTML = error;
      thisForm.querySelector('.error-message').classList.add('d-block');
    }
  
    // Display selected files in input file
    $('.input-file').change(function() {
      files_name = []
      for (file in this.files)
        files_name.push(file.name)
      
      $(this).prev('.input-file-label').val(files_name.join(', '))
    });

  })();
  