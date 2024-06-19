import strokeDuoIcon from 'icons/stroke-duo.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BookingIsDuoCell.module.scss'

export const BookingIsDuoCell = ({ isDuo }: { isDuo: boolean }) =>
  isDuo ? (
    <SvgIcon
      src={strokeDuoIcon}
      alt="Réservation DUO"
      className={styles['bookings-duo-icon']}
    />
  ) : (
    <></>
  )
