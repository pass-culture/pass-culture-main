import React from 'react'

import strokeSearchIcon from 'icons/stroke-search.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoFilteredBookings.module.scss'

interface NoFilteredBookingsProps {
  resetFilters: () => void
}

export const NoFilteredBookings = ({
  resetFilters,
}: NoFilteredBookingsProps) => (
  <div className={styles['no-filtered-bookings-wrapper']}>
    <SvgIcon
      src={strokeSearchIcon}
      alt=""
      className={styles['nfb-icon']}
      width="124"
    />
    <span>Aucune réservation trouvée pour votre recherche</span>
    <span>Vous pouvez modifier votre recherche ou</span>
    <button onClick={resetFilters} type="button">
      afficher toutes les réservations
    </button>
  </div>
)
