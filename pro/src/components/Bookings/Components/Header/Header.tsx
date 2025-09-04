import { pluralize } from '@/commons/utils/pluralize'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'

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
            {pluralize(bookingsRecapFilteredLength, 'réservation')}
          </span>
        ) : (
          <Button
            variant={ButtonVariant.TERNARY}
            onClick={resetBookings}
            icon={fullRefreshIcon}
            iconPosition={IconPositionEnum.LEFT}
          >
            Voir toutes les réservations
          </Button>
        )}
      </div>
    )
  }
}
