import React from 'react'

import { Audience } from 'core/shared/types'
import strokeBookingHold from 'icons/stroke-booking-hold.svg'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoData.module.scss'

interface NoOffers {
  page: 'offers' | 'bookings'
  audience: Audience
}

const wordingMapping = {
  offers: {
    icon: strokeNoBookingIcon,
    [Audience.INDIVIDUAL]: 'Vous n’avez pas encore créé d’offre',
    [Audience.COLLECTIVE]: 'Vous n’avez pas encore créé d’offre',
  },
  bookings: {
    icon: strokeBookingHold,
    [Audience.INDIVIDUAL]: 'Vous n’avez aucune réservation pour le moment',
    [Audience.COLLECTIVE]:
      'Vous n’avez aucune réservation collective pour le moment',
  },
}

const NoOffers = ({ page, audience }: NoOffers): JSX.Element => {
  return (
    <div className={styles['no-data']}>
      <SvgIcon
        src={wordingMapping[page].icon}
        alt=""
        className={styles['no-data-icon']}
        viewBox="0 0 200 156"
      />
      <p>{wordingMapping[page][audience]}</p>
    </div>
  )
}

export default NoOffers
