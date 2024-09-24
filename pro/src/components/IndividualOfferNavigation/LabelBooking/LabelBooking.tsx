import { useTranslation } from 'react-i18next'

import styles from './LabelBooking.module.scss'

type LabelBooking = {
  bookingsCount: number
}

export function LabelBooking({ bookingsCount }: LabelBooking) {
  const { t } = useTranslation('common')

  return (
    <>
      {t('reservations')}
      {bookingsCount > 0 && (
        <span className={styles['bookings-count']}>
          {new Intl.NumberFormat('fr-FR').format(bookingsCount)}
        </span>
      )}
    </>
  )
}
