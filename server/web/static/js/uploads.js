(function () {
    "use strict";
  
    let btnFilterRecordings = document.querySelectorAll('.filter-recordings');
    let btnFilterRequest = document.querySelectorAll('.filter-request');
    let btnsManageRequest = document.querySelectorAll('.btn-view-request, ' +
                                                      '.btn-delete-request');
    let btnCreateRequest = document.querySelector('.btn-create-request');
    let btnDeleteRequest = document.querySelector('.btn-delete-request');
    let recordingsCell = document.querySelectorAll('.portfolio-item');

    btnFilterRecordings.forEach( function(e) {
        e.addEventListener('click', function(event) {
            for (const btn of btnsManageRequest) {
                btn.classList.add('btn-request-hidden');
                btn.setAttribute('request', '');
            }
        });
    });

    btnFilterRequest.forEach( function(e) {
        e.addEventListener('click', function(event) {
            let request_id = event.target.getAttribute('data-filter').replace('.filter-request', '');
            for (const btn of btnsManageRequest) {
                btn.classList.remove('btn-request-hidden');
                btn.setAttribute('request', request_id);
            }
        });
    });

    recordingsCell.forEach( function(e) {
        let recordingInfos = e.querySelector('.portfolio-info');
        let btnRecordingSelect = e.querySelector('.portfolio-links .bx-pointer');
        btnRecordingSelect.addEventListener('click', function(event) {
            let isSelected = (e.getAttribute('selected') === 'true');
            recordingInfos.style.opacity = isSelected ? '' : '1';
            recordingInfos.style.background = isSelected ? '' : 'rgba(36, 135, 206, 0.6)';
            e.setAttribute('selected', !isSelected);

            if (!isSelected)
                btnCreateRequest.classList.remove('btn-request-hidden');
            else {
                let createRequestIsEnabled = false;
                for (const cell of recordingsCell) {
                    if (cell.getAttribute('selected') === 'true') {
                        createRequestIsEnabled = true;
                        break;
                    }
                }
                if (createRequestIsEnabled)
                    btnCreateRequest.classList.remove('btn-request-hidden');
                else
                    btnCreateRequest.classList.add('btn-request-hidden');
            }
        });
    });

    btnCreateRequest.addEventListener( 'click', function(event) {
        event.preventDefault();

        let data = { 'recordings': [] }
        for (const cell of recordingsCell) {
            if (cell.getAttribute('selected') === 'true')
                data['recordings'].add(cell.getAttribute('recording'));
        }

        send_request_action('/create_request/', data, location.reload);
    });

    btnDeleteRequest.addEventListener( 'click', function(event) {
        event.preventDefault();
        let request_id = event.getAttribute('request');
        send_request_action('/delete_request/' + request_id + '/', {}, location.reload);
    });

    function send_request_action(action, data, successCallback) {
        fetch(action, {
            method: 'POST',
            body: data,
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
                successCallback();
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
  