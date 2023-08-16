(function () {
    "use strict";
  
    let btnFilterSolutions = document.querySelectorAll('.filter-solutions');
    let btnFilterSolution = document.querySelectorAll('.filter-solution');
    let btnViewAccount = document.querySelector('.btn-view-account');
    let btnAddFavorite = document.querySelector('.btn-add-favorite');
    let btnRemoveFavorite = document.querySelector('.btn-remove-favorite');

    btnFilterSolutions.forEach( function(e) {
        e.addEventListener('click', function(event) {
            btnViewAccount.classList.add('btn-account-hidden');
            btnViewAccount.setAttribute('account', '');
            let newHref = '/' + btnViewAccount.getAttribute('href').split('/')[1] + '/'
            btnViewAccount.setAttribute('href', newHref);
        });
    });

    btnFilterSolution.forEach( function(e) {
        e.addEventListener('click', function(event) {
            let account = event.target.getAttribute('account');
            btnViewAccount.classList.remove('btn-account-hidden');
            btnViewAccount.setAttribute('account', account);
            let newHref = '/' + btnViewAccount.getAttribute('href').split('/')[1] + '/' + account + '/'
            btnViewAccount.setAttribute('href', newHref);
        });
    });

    if (btnAddFavorite !== null) {
        btnAddFavorite.addEventListener('click', function(event) {
            event.preventDefault();

            let recording = event.target.getAttribute('recording');
            let url = recording !== null ?
                        '/add_recording_favorite/' + recording + '/' :
                        '/add_request_favorite/' + event.target.getAttribute('request') + '/'
            let data = { solution: event.target.getAttribute('solution') }

            send_favorite_action(url, data, event.target, function() {
                btnRemoveFavorite.setAttribute('enabled', 'true');
            });
        });
    }

    if (btnRemoveFavorite !== null) {
        btnRemoveFavorite.addEventListener('click', function(event) {
            event.preventDefault();

            let recording = event.target.getAttribute('recording');
            let url = recording !== null ?
                        '/remove_recording_favorite/' + recording + '/' :
                        '/remove_request_favorite/' + event.target.getAttribute('request') + '/'
            let data = { solution: event.target.getAttribute('solution') }

            send_favorite_action(url, data, event.target, function() {
                btnAddFavorite.setAttribute('enabled', 'true');
            });
        });
    }

    function send_favorite_action(action, data, target, successCallback) {
        target.setAttribute('enabled', 'false');

        data['csrfmiddlewaretoken'] = getCsrfToken()
        fetch(action, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: { 
                'X-Requested-With': 'XMLHttpRequest', 
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (response.ok)
                successCallback();
            else
                target.setAttribute('enabled', 'true');
        })
      }
})();
  