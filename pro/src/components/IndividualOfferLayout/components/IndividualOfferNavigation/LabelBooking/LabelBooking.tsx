import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import styles from './LabelBooking.module.scss'

type LabelBookingProps = {
  bookingsCount: number
}

export function LabelBooking({ bookingsCount }: Readonly<LabelBookingProps>) {
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  return (
    <>
      Réservations
      {bookingsCount > 0 && !isOfferExposureEnabled && (
        <span className={styles['bookings-count']}>
          {new Intl.NumberFormat('fr-FR').format(bookingsCount)}
        </span>
      )}
    </>
  )
}
