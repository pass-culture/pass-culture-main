import cx from 'classnames'

import { GetBookingResponse } from 'apiClient/v2'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import strokeDuoIcon from 'icons/stroke-duo.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BookingDetails.module.scss'

interface BookingProps {
  label: string
  value: number | string
}

const BookingDetailsLine = ({ label, value }: BookingProps) => (
  <div>
    <div className={styles['desk-label']}>{label}</div>
    <div className={styles['desk-value']}>{value}</div>
  </div>
)

interface BookingDetailsProps {
  booking: GetBookingResponse
}

const formattedBookingDate = (booking: GetBookingResponse): string => {
  return !booking.datetime
    ? 'Permanent'
    : formatLocalTimeDateString(
        booking.datetime,
        booking.offerDepartmentCode || undefined,
        "dd/MM/yyyy - HH'h'mm"
      )
}

export const BookingDetails = ({ booking }: BookingDetailsProps) => {
  return (
    <div className={styles['booking-summary']}>
      <BookingDetailsLine label="Utilisateur : " value={booking.userName} />
      <BookingDetailsLine label="Offre : " value={booking.offerName} />
      <BookingDetailsLine
        label="Date de l’offre : "
        value={formattedBookingDate(booking)}
      />

      {booking.quantity === 2 ? (
        <div>
          <div className={styles['desk-label']}>{'Prix : '}</div>
          <div className={cx(styles['desk-value'], styles['duo-price'])}>
            {`${booking.price * 2} €`}
            <SvgIcon src={strokeDuoIcon} alt="Réservation DUO" />
          </div>
        </div>
      ) : (
        <BookingDetailsLine label="Prix : " value={`${booking.price} €`} />
      )}
      {booking.priceCategoryLabel && (
        <BookingDetailsLine
          label="Intitulé du tarif : "
          value={booking.priceCategoryLabel}
        />
      )}
      {booking.ean13 && (
        <BookingDetailsLine label="EAN-13 : " value={booking.ean13} />
      )}
    </div>
  )
}
