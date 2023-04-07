import React from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'

import styles from './BookingIsDuoCell.module.scss'

const BookingIsDuoCell = ({ isDuo }: { isDuo: boolean }) => {
  return (
    <span className={styles['bookings-duo-icon']}>
      {isDuo && <DuoSvg title="Réservation DUO" />}
    </span>
  )
}

export default BookingIsDuoCell
