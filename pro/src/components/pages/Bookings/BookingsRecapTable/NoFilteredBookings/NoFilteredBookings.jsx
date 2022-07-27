import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const NoFilteredBookings = ({ resetFilters }) => {
  return (
    <div className="no-filtered-bookings-wrapper">
      <Icon className="nfb-icon" svg="ico-search-gray" />
      <span>Aucune réservation trouvée pour votre recherche</span>
      <span>Vous pouvez modifier votre recherche ou</span>
      <button onClick={resetFilters} type="button">
        afficher toutes les réservations
      </button>
    </div>
  )
}

NoFilteredBookings.propTypes = {
  resetFilters: PropTypes.func.isRequired,
}

export default NoFilteredBookings
