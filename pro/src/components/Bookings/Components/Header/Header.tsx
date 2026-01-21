import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'

import styles from './Header.module.scss'

export interface HeaderProps {
  bookingsRecapFilteredLength: number
  isLoading: boolean
  queryBookingId?: string
  resetBookings: () => void
}

export const Header = ({
  bookingsRecapFilteredLength,
  isLoading,
  queryBookingId,
  resetBookings,
}: HeaderProps) => {
  if (isLoading) {
    return (
      <div className={styles['bookings-header-loading']}>
        Chargement des réservations...
      </div>
    )
  } else {
    return (
      <div className={styles['bookings-header']}>
        {!queryBookingId ? (
          <span className={styles['bookings-header-number']}>
            {bookingsRecapFilteredLength}{' '}
            {pluralizeFr(
              bookingsRecapFilteredLength,
              'réservation',
              'réservations'
            )}
          </span>
        ) : (
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={resetBookings}
            icon={fullRefreshIcon}
            iconPosition={IconPositionEnum.LEFT}
            label="Voir toutes les réservations"
          />
        )}
      </div>
    )
  }
}
