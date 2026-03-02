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

/* ---------------- helpers ---------------- */

const formattedBookingDate = (booking: GetBookingResponse): string =>
  !booking.datetime
    ? 'Permanent'
    : formatLocalTimeDateString(
        booking.datetime,
        booking.offerDepartmentCode || undefined,
        "dd/MM/yyyy - HH'h'mm"
      )

const getFormattedPrice = (
  price: number,
  isCaledonian: boolean | undefined
): string => {
  return isCaledonian
    ? formatPacificFranc(convertEuroToPacificFranc(price))
    : formatPrice(price)
}

/* ---------------- component ---------------- */

export const BookingDetails = ({ booking }: BookingDetailsProps) => {
  const isCaledonian = useIsCaledonian()

  const baseFields = [
    { label: 'Utilisateur : ', value: booking.userName },
    { label: 'Offre : ', value: booking.offerName },
    {
      label: 'Date de l’offre : ',
      value: formattedBookingDate(booking),
    },
  ]

  const optionalFields = [
    booking.priceCategoryLabel && {
      label: 'Intitulé du tarif : ',
      value: booking.priceCategoryLabel,
    },
    booking.ean13 && {
      label: 'EAN-13 : ',
      value: booking.ean13,
    },
  ].filter(Boolean) as BookingProps[]

  const totalPrice = booking.quantity === 2 ? booking.price * 2 : booking.price

  const formattedPrice = getFormattedPrice(totalPrice, isCaledonian)

  return (
    <div className={styles['booking-summary']}>
      {baseFields.map((field) => (
        <BookingDetailsLine key={field.label} {...field} />
      ))}

      {booking.quantity === 2 ? (
        <div className={styles['desk-line']}>
          <div className={styles['desk-label']}>Prix :</div>
          <div className={styles['desk-value']}>{formattedPrice}</div>
          <SvgIcon src={strokeDuoIcon} alt="Réservation DUO" width="30" />
        </div>
      ) : (
        <BookingDetailsLine label="Prix : " value={formattedPrice} />
      )}

      {optionalFields.map((field) => (
        <BookingDetailsLine key={field.label} {...field} />
      ))}
    </div>
  )
}
