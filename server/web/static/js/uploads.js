(function () {
    "use strict";
  
    let btnFilterRecordings = document.querySelectorAll('.filter-recordings');
    btnFilterRecordings.forEach( function(e) {
        e.addEventListener('click', function(event) {
            let btnsManageRequest = document.querySelectorAll('.btn-view-request, ' +
                                                              '.btn-delete-request');
            for (const btn of btnsManageRequest) {
                btn.classList.add('btn-request-hidden');
                let newHref = '/' + btn.getAttribute('href').split('/')[1] + '/'
                btn.setAttribute('href', newHref);
            }
        });
    });

    let btnFilterRequest = document.querySelectorAll('.filter-request');
    btnFilterRequest.forEach( function(e) {
        e.addEventListener('click', function(event) {
            let request_id = event.target.getAttribute('data-filter').replace('.filter-request', '');
            let btnsManageRequest = document.querySelectorAll('.btn-view-request, ' +
                                                              '.btn-delete-request');
            for (const btn of btnsManageRequest) {
                btn.classList.remove('btn-request-hidden');
                let newHref = '/' + btn.getAttribute('href').split('/')[1] + '/' + request_id + '/'
                btn.setAttribute('href', newHref);
            }
        });
    });
    
    let recordingInfos = document.querySelectorAll('.portfolio-info');
    recordingInfos.forEach( function(e) {
        let btnRecordingSelect = e.querySelector('.portfolio-links .bx-pointer');
        btnRecordingSelect.addEventListener('click', function(event) {
            isSelected = (e.style.opacity === '1');
            e.style.opacity = isSelected ? '0' : '1';
            e.style.background = isSelected ? '' : 'rgba(36, 135, 206, 0.6)';
        });
    });
  })();
  