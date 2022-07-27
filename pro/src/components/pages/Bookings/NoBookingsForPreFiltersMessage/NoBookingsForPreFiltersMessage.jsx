import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const NoBookingsForPreFiltersMessage = ({ resetPreFilters }) => (
  <div className="br-warning no-bookings-for-pre-filters">
    <Icon svg="ico-search-gray" />
    <p>Aucune réservation trouvée pour votre recherche.</p>
    <p>
      {'Veuillez modifier vos filtres et lancer une nouvelle recherche ou '}
      <button
        className="tertiary-button reset-filters-link"
        onClick={resetPreFilters}
        type="button"
      >
        réinitialiser tous les filtres.
      </button>
    </p>
  </div>
)

NoBookingsForPreFiltersMessage.propTypes = {
  resetPreFilters: PropTypes.func.isRequired,
}

export default NoBookingsForPreFiltersMessage
