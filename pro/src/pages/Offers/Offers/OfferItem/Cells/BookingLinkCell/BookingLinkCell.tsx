import React from 'react'

import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as ArrowIcon } from 'icons/ico-arrow-right.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'

import styles from '../../OfferItem.module.scss'

interface IBookingLinkCellProps {
  bookingId: string
  bookingStatus: string
  offerEventDate?: Date | null
}

const BookingLinkCell = ({
  bookingId,
  bookingStatus,
  offerEventDate,
}: IBookingLinkCellProps) => {
  if (!offerEventDate) {
    return null
  }
  const { logEvent } = useAnalytics()
  const eventDateFormated = formatBrowserTimezonedDateAsUTC(
    offerEventDate,
    FORMAT_ISO_DATE_ONLY
  )
  const bookingLink = `/reservations/collectives?page=1&offerEventDate=${eventDateFormated}&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=${bookingId}`
  return (
    <td className={styles['booking-link-column']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        className={styles['button']}
        link={{ isExternal: false, to: bookingLink }}
        Icon={ArrowIcon}
        iconPosition={IconPositionEnum.CENTER}
        onClick={() =>
          logEvent?.(CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING, {
            from: location.pathname,
          })
        }
        hasTooltip
      >
        Voir la {bookingStatus == 'PENDING' ? 'préréservation' : 'réservation'}
      </ButtonLink>
    </td>
  )
}

export default BookingLinkCell
