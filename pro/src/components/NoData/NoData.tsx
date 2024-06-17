import React from 'react'

import strokeBookingHold from 'icons/stroke-booking-hold.svg'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoData.module.scss'

interface NoDataProps {
  page: 'offers' | 'bookings'
}

export const NoData = ({ page }: NoDataProps): JSX.Element => {
  return (
    <div className={styles['no-data']}>
      <SvgIcon
        src={page === 'offers' ? strokeNoBookingIcon : strokeBookingHold}
        alt=""
        className={styles['no-data-icon']}
      />
      <p>
        {page === 'offers'
          ? 'Vous n’avez pas encore créé d’offre'
          : 'Vous n’avez aucune réservation pour le moment'}
      </p>
    </div>
  )
}
