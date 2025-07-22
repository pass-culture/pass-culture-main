import styles from './LabelBooking.module.scss'

type LabelBookingProps = {
  bookingsCount: number
}

export function LabelBooking({ bookingsCount }: Readonly<LabelBookingProps>) {
  return (
    <>
      Réservations
      {bookingsCount > 0 && (
        <span className={styles['bookings-count']}>
          {new Intl.NumberFormat('fr-FR').format(bookingsCount)}
        </span>
      )}
    </>
  )
}
