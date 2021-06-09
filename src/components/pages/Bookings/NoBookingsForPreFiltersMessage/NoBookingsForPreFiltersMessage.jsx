import React from 'react'

import Icon from 'components/layout/Icon'

const NoBookingsForPreFiltersMessage = () => (
  <div className="br-warning no-bookings-for-pre-filters">
    <Icon svg="ico-search-gray" />
    <p>
      {'Aucune réservation trouvée pour votre recherche.'}
    </p>
    <p>
      {
        'Veuillez modifier vos filtres et lancer une nouvelle recherche ou réinitialiser tout les filtres.'
      }
    </p>
  </div>
)

export default NoBookingsForPreFiltersMessage
