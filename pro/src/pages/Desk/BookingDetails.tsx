import type { GetBookingResponse } from '@/apiClient/v1'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { formatPrice } from '@/commons/utils/formatPrice'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import strokeDuoIcon from '@/icons/stroke-duo.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './BookingDetails.module.scss'

interface BookingProps {
  label: string
  value: number | string
}

const BookingDetailsLine = ({ label, value }: BookingProps) => (
  <div className={styles['desk-line']}>
    <div className={styles['desk-label']}>{label}</div>
    <div>{value}</div>
  </div>
)

export interface BookingDetailsProps {
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
  const isCaledonian = useIsCaledonian()

  return (
    <div className={styles['booking-summary']}>
      <BookingDetailsLine label="Utilisateur : " value={booking.userName} />
      <BookingDetailsLine label="Offre : " value={booking.offerName} />
      <BookingDetailsLine
        label="Date de l’offre : "
        value={formattedBookingDate(booking)}
      />

      {booking.quantity === 2 ? (
        <div className={styles['desk-line']}>
          <div className={styles['desk-label']}>Prix :</div>
          <div className={styles['desk-value']}>
            {isCaledonian
              ? formatPacificFranc(convertEuroToPacificFranc(booking.price * 2))
              : formatPrice(booking.price * 2)}
          </div>
          <SvgIcon src={strokeDuoIcon} alt="Réservation DUO" width="30" />
        </div>
      ) : (
        <BookingDetailsLine
          label="Prix : "
          value={
            isCaledonian
              ? formatPacificFranc(convertEuroToPacificFranc(booking.price))
              : formatPrice(booking.price)
          }
        />
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
