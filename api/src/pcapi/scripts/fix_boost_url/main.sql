UPDATE
    boost_cinema_details
SET
    "cinemaUrl" = REPLACE(
        "cinemaUrl",
        '.boostbilletterie.fr',
        '.cinegroup.pro'
    );
