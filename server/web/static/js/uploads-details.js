(function () {
    "use strict";
  
    let btnFilterSolutions = document.querySelectorAll('.filter-solutions');
    let btnFilterSolution = document.querySelectorAll('.filter-solution');
    let btnViewAccount = document.querySelector('.btn-view-account');
    let btnFavorite = document.querySelector('.btn-favorite');

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
            let account_id = event.target.getAttribute('account');
            btnViewAccount.classList.remove('btn-account-hidden');
            btnViewAccount.setAttribute('account', account_id);
            let newHref = '/' + btnViewAccount.getAttribute('href').split('/')[1] + '/' + account_id + '/'
            btnViewAccount.setAttribute('href', newHref);
        });
    });

    if (btnFavorite !== null) {
        btnFavorite.addEventListener('click', function(event) {
            return;
        });
    }
})();
  