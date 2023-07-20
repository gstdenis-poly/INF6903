(function () {
    "use strict";
  
    let forms = document.querySelectorAll('.login-form, .register-form');
  
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
        login_form_submit(thisForm, action, formData);
      });
    });
  
    function login_form_submit(thisForm, action, formData) {
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
            location.reload();
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
  
  })();
  