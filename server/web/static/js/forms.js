(function () {
    "use strict";
  
    let forms = document.querySelectorAll('.login-form, ' + 
                                          '.register-form, ' + 
                                          '.edit-account-form, ' + 
                                          '.upload-recordings-form, ' +
                                          '.edit-recording-form');
  
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
        let successMessage = thisForm.querySelector('.success-message');
        if (successMessage !== null)
          successMessage.classList.remove('d-block');
  
        let formData = new FormData( thisForm );
        form_submit(thisForm, action, formData);
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
          let successMessage = thisForm.querySelector('.success-message');
          if (successMessage === null)
            location.href = '';
          else
            successMessage.classList.add('d-block');
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
    let inputFiles = document.querySelectorAll('.input-file');
    inputFiles.forEach( function(e) {
      e.addEventListener('change', function(event) {
        event.preventDefault();
    
        let targetInput = event.target;

        let files_name = [];
        for (let i = 0; i < targetInput.files.length; i++)
          files_name.push(targetInput.files[i].name);

        if (files_name.length > 0)
          this.previousElementSibling.innerHTML = files_name.join(', ');
      });
    });

  })();
  