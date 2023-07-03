import React from 'react'

import { Audience } from 'core/shared'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoData.module.scss'

interface NoOffers {
  page: 'offers' | 'bookings'
  audience: Audience
}

const wordingMapping = {
  offers: {
    [Audience.INDIVIDUAL]: 'Vous n’avez pas encore créé d’offre',
    [Audience.COLLECTIVE]: 'Vous n’avez pas encore créé d’offre',
  },
  bookings: {
    [Audience.INDIVIDUAL]: 'Vous n’avez aucune réservation pour le moment',
    [Audience.COLLECTIVE]:
      'Vous n’avez aucune réservation collective pour le moment',
  },
}

const NoOffers = ({ page, audience }: NoOffers): JSX.Element => {
  return (
    <div className={styles['no-data']}>
      <SvgIcon
        src={strokeNoBookingIcon}
        alt=""
        className={styles['no-data-icon']}
        viewBox="0 0 200 156"
        width="100"
      />
      <p>{wordingMapping[page][audience]}</p>
    </div>
  )
}

export default NoOffers
