import React from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../layout/Icon'

const NoFilteredBookings = ({ setFilters }) => {
  function resetFilters() {
    setFilters({
      offerName: ''
    })
  }

  return (
    <div className='no-filtered-bookings-wrapper'>
      <Icon
        className='nfb-icon'
        svg="ico-search"
      />
      <span>
        {'Aucune réservation trouvée pour votre recherche'}
      </span>
      <span>
        {'Vous pouvez modifier votre recherche ou'}
      </span>
      <button
        onClick={resetFilters}
        type="button"
      >
        {'afficher toutes les réservations'}
      </button>
    </div>
  )
}

NoFilteredBookings.propTypes = {
  setFilters: PropTypes.func.isRequired,
}

export default NoFilteredBookings
