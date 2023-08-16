(function () {
    "use strict";
  
    let btnFilterSolutions = document.querySelectorAll('.filter-solutions');
    let btnFilterSolution = document.querySelectorAll('.filter-solution');
    let btnViewAccount = document.querySelector('.btn-view-account');
    let btnAddFavorite = document.querySelectorAll('.btn-add-favorite');
    let btnRemoveFavorite = document.querySelectorAll('.btn-remove-favorite');

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

    btnAddFavorite.forEach( function(e, i) {
        e.addEventListener('click', function(event) {
            event.preventDefault();

            send_favorite_action('/add_favorite/', event.target.parentElement, function() {
                btnRemoveFavorite[i].setAttribute('enabled', 'true');
            });
        });
    });

    btnRemoveFavorite.forEach( function(e, i) {
        e.addEventListener('click', function(event) {
            event.preventDefault();

            send_favorite_action('/remove_favorite/', event.target.parentElement, function() {
                btnAddFavorite[i].setAttribute('enabled', 'true');
            });
        });
    });

    function send_favorite_action(action, target, successCallback) {
        target.setAttribute('enabled', 'false');

        fetch(action, {
            method: 'POST',
            body: JSON.stringify({
                csrfmiddlewaretoken: getCsrfToken(),
                recording: target.getAttribute('recording'), 
                solution: target.getAttribute('solution') 
            }),
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
  