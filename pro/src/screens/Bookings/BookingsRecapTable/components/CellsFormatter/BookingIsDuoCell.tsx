import React from 'react'

import strokeDuoIcon from 'icons/stroke-duo.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BookingIsDuoCell.module.scss'

const BookingIsDuoCell = ({ isDuo }: { isDuo: boolean }) => {
  return isDuo ? (
    <SvgIcon
      src={strokeDuoIcon}
      alt="Réservation DUO"
      className={styles['bookings-duo-icon']}
    />
  ) : (
    <></>
  )
}

export default BookingIsDuoCell
