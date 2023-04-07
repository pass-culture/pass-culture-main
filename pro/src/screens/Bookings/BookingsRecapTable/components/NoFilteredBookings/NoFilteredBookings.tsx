import React from 'react'

import Icon from 'ui-kit/Icon/Icon'

import styles from './NoFilteredBookings.module.scss'

interface NoFilteredBookingsProps {
  resetFilters: () => void
}

const NoFilteredBookings = ({ resetFilters }: NoFilteredBookingsProps) => {
  return (
    <div className={styles['no-filtered-bookings-wrapper']}>
      <Icon className={styles['nfb-icon']} svg="ico-search-gray" />
      <span>Aucune réservation trouvée pour votre recherche</span>
      <span>Vous pouvez modifier votre recherche ou</span>
      <button onClick={resetFilters} type="button">
        afficher toutes les réservations
      </button>
    </div>
  )
}

export default NoFilteredBookings
