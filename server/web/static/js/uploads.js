(function () {
    "use strict";
  
    let btnFilterRecordings = document.querySelectorAll('.filter-recordings');
    let btnFilterRequest = document.querySelectorAll('.filter-request');
    let btnsManageRequest = document.querySelectorAll('.btn-view-request, ' +
                                                      '.btn-delete-request');
    let btnCreateRequest = document.querySelectorAll('.btn-create-request');
    let recordingsCell = document.querySelectorAll('.portfolio-info');

    btnFilterRecordings.forEach( function(e) {
        e.addEventListener('click', function(event) {
            for (const btn of btnsManageRequest) {
                btn.classList.add('btn-request-hidden');
                let newHref = '/' + btn.getAttribute('href').split('/')[1] + '/'
                btn.setAttribute('href', newHref);
            }
        });
    });

    btnFilterRequest.forEach( function(e) {
        e.addEventListener('click', function(event) {
            let request_id = event.target.getAttribute('data-filter').replace('.filter-request', '');
            for (const btn of btnsManageRequest) {
                btn.classList.remove('btn-request-hidden');
                let newHref = '/' + btn.getAttribute('href').split('/')[1] + '/' + request_id + '/'
                btn.setAttribute('href', newHref);
            }
        });
    });

    recordingsCell.forEach( function(e) {
        let btnRecordingSelect = e.querySelector('.portfolio-links .bx-pointer');
        btnRecordingSelect.addEventListener('click', function(event) {
            let isSelected = (e.style.opacity === '1');
            e.style.opacity = isSelected ? '' : '1';
            e.style.background = isSelected ? '' : 'rgba(36, 135, 206, 0.6)';

            if (!isSelected)
                btnCreateRequest.classList.remove('btn-request-hidden');
            else {
                let createRequestIsEnabled = false;
                for (const cell of recordingsCell) {
                    if (cell.style.opacity === '1') {
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
  })();
  