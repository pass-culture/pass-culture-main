import cx from 'classnames'
import React from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'
import { formatLocalTimeDateString } from 'utils/timezone'

import { IBooking } from '..'

import styles from './BookingDetails.module.scss'

interface IBookingDetailsProps {
  booking: IBooking | null
}

const BookingDetails = ({
  booking,
}: IBookingDetailsProps): JSX.Element | null => {
  const formattedBookingDate = (booking: IBooking): string => {
    return !booking.datetime
      ? 'Permanent'
      : formatLocalTimeDateString(
          booking.datetime,
          booking.venueDepartmentCode,
          "dd/MM/yyyy - HH'h'mm"
        )
  }

  if (!booking) {
    return null
  }

  return (
    <div
      aria-live="polite"
      aria-relevant="all"
      className={styles['booking-summary']}
    >
      <div>
        <div className={styles['desk-label']}>{'Utilisateur : '}</div>
        <div className={styles['desk-value']}>{booking.userName}</div>
      </div>
      <div>
        <div className={styles['desk-label']}>{'Offre : '}</div>
        <div className={styles['desk-value']}>{booking.offerName}</div>
      </div>
      <div>
        <div className={styles['desk-label']}>{'Date de l’offre : '}</div>
        <div className={styles['desk-value']}>
          {formattedBookingDate(booking)}
        </div>
      </div>
      {booking.quantity === 2 ? (
        <div>
          <div className={styles['desk-label']}>{'Prix : '}</div>
          <div className={cx(styles['desk-value'], styles['duo-price'])}>
            {`${booking.price * 2} €`}
            <DuoSvg title="Réservation DUO" />
          </div>
        </div>
      ) : (
        <div>
          <div className={styles['desk-label']}>{'Prix : '}</div>
          <div className={styles['desk-value']}>{`${booking.price} €`}</div>
        </div>
      )}
      {booking.ean13 !== null && (
        <div>
          <div className={styles['desk-label']}>{'ISBN : '}</div>
          <div className={styles['desk-value']}>{booking.ean13}</div>
        </div>
      )}
    </div>
  )
}

export default BookingDetails
