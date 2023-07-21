(function () {
    "use strict";
  
    let btnFilterRecordings = document.querySelectorAll('.filter-recordings');
    btnFilterRecordings.forEach( function(e) {
        e.addEventListener('click', function(event) {
            let btnsManageRequest = document.querySelectorAll('.btn-view-request, ' +
                                                              '.btn-delete-request');
            for (const btn of btnsManageRequest) {
                btn.classList.add('btn-request-hidden');
                btn.href = '/' + btn.href.split('/')[1] + '/'
            }
        });
    });

    let btnFilterRequest = document.querySelectorAll('.filter-request');
    btnFilterRequest.forEach( function(e) {
        e.addEventListener('click', function(event) {
            console.log(event.target.getAttribute('data-filter'));
            //request_id = event.target.getAttribute('data-filter').replace('.filter-request', '');
            let btnsManageRequest = document.querySelectorAll('.btn-view-request, ' +
                                                              '.btn-delete-request');
            for (const btn of btnsManageRequest) {
                btn.classList.remove('btn-request-hidden');
                btn.href = '/' + btn.href.split('/')[1] + '/' + request_id + '/'
            }
        });
    });
    
  })();
  