import cx from 'classnames'
import React from 'react'

import strokeDuoIcon from 'icons/stroke-duo.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatLocalTimeDateString } from 'utils/timezone'

import { IBooking } from '..'

import styles from './BookingDetails.module.scss'

interface BookingDetailsLine {
  label: string
  value: number | string
}

const BookingDetailsLine = ({ label, value }: BookingDetailsLine) => (
  <div>
    <div className={styles['desk-label']}>{label}</div>
    <div className={styles['desk-value']}>{value}</div>
  </div>
)

interface BookingDetailsProps {
  booking: IBooking | null
}

const BookingDetails = ({
  booking,
}: BookingDetailsProps): JSX.Element | null => {
  /* istanbul ignore next: DEBT, TO FIX */
  const formattedBookingDate = (booking: IBooking): string => {
    return !booking.datetime
      ? 'Permanent'
      : formatLocalTimeDateString(
          booking.datetime,
          booking.venueDepartmentCode || undefined,
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
      <BookingDetailsLine label="Utilisateur : " value={booking.userName} />
      <BookingDetailsLine label="Offre : " value={booking.offerName} />
      <BookingDetailsLine
        label="Date de l’offre : "
        value={formattedBookingDate(booking)}
      />

      {
        /* istanbul ignore next: DEBT, TO FIX */
        booking.quantity === 2 ? (
          <div>
            <div className={styles['desk-label']}>{'Prix : '}</div>
            <div className={cx(styles['desk-value'], styles['duo-price'])}>
              {`${booking.price * 2} €`}
              <SvgIcon src={strokeDuoIcon} alt="Réservation DUO" />
            </div>
          </div>
        ) : (
          <BookingDetailsLine label="Prix : " value={`${booking.price} €`} />
        )
      }
      {booking.priceCategoryLabel && (
        <BookingDetailsLine
          label="Intitulé du tarif : "
          value={booking.priceCategoryLabel}
        />
      )}
      {booking.ean13 && (
        <BookingDetailsLine label="ISBN : " value={booking.ean13} />
      )}
    </div>
  )
}

export default BookingDetails
