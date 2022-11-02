import React from 'react'

import { Audience } from 'core/shared'
import Icon from 'ui-kit/Icon/Icon'

import styles from './NoData.module.scss'

interface INoData {
  page: 'offers' | 'bookings'
  audience: Audience
}

const wordingMapping = {
  offers: {
    [Audience.INDIVIDUAL]: 'Vous n’avez pas encore créé d’offre.',
    [Audience.COLLECTIVE]: 'Vous n’avez pas encore créé d’offre.',
  },
  bookings: {
    [Audience.INDIVIDUAL]: 'Vous n’avez aucune réservation pour le moment',
    [Audience.COLLECTIVE]:
      'Vous n’avez aucune réservation collective pour le moment',
  },
}

const NoData = ({ page, audience }: INoData): JSX.Element => {
  return (
    <div className={styles['no-data']}>
      <Icon className={styles['no-data-icon']} svg="ticket-cross" />
      <p>{wordingMapping[page][audience]}</p>
    </div>
  )
}

export default NoData
