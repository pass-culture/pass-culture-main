import styles from './LabelBooking.module.scss'

type LabelBooking = {
  bookingsCount: number
}

export function LabelBooking({ bookingsCount }: LabelBooking) {
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
