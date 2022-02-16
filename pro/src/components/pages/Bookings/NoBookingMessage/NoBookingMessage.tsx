/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import React from 'react'

import { ReactComponent as NoBookingIconSvg } from 'icons/ticket-cross.svg'

import styles from './NoBookingMessage.module.scss'

const NoBookingMessage = (): JSX.Element => {
  return (
    <div className="br-warning">
      <NoBookingIconSvg aria-hidden />
      <p className={styles['no-booking-message']}>
        Vous n’avez aucune réservation pour le moment
      </p>
    </div>
  )
}

export default NoBookingMessage
