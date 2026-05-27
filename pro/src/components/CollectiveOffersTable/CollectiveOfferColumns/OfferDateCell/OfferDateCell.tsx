import type { GetVenueResponseModel } from '@/apiClient/v1'
import {
  type CollectiveOffer,
  isCollectiveOfferBookable,
} from '@/commons/core/OfferEducational/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import {
  formatShortDateForInput,
  getDateTimeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import styles from './OfferDateCell.module.scss'

export interface OfferEventDateCellProps {
  offer: CollectiveOffer
}

function getBookableOfferDate(
  date: string,
  venue: GetVenueResponseModel
): Date {
  return getLocalDepartementDateTimeFromUtc(date, venue.location.departmentCode)
}

export const OfferDateCell = ({ offer }: OfferEventDateCellProps) => {
  const isTemplateTable = !isCollectiveOfferBookable(offer)
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const getFormattedDatesForOffer = (offer: CollectiveOffer) => {
    const offerDatetimes = offer.dates

    const options: Intl.DateTimeFormatOptions = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }

    if (!offerDatetimes?.start || !offerDatetimes.end) {
      if (isTemplateTable) {
        return ['Toute l’année scolaire']
      }
      return ['-']
    }
    const offerStartDate = isTemplateTable
      ? toDateStrippedOfTimezone(offerDatetimes.start)
      : getBookableOfferDate(offerDatetimes.start, selectedPartnerVenue)
    const offerEndDate = isTemplateTable
      ? toDateStrippedOfTimezone(offerDatetimes.end)
      : getBookableOfferDate(offerDatetimes.end, selectedPartnerVenue)

    if (
      offerDatetimes.start === offerDatetimes.end ||
      (isTemplateTable &&
        formatShortDateForInput(offerStartDate) ===
          formatShortDateForInput(offerEndDate))
    ) {
      return [`${getDateTimeToFrenchText(offerStartDate, options)}`]
    }

    return [
      `Du ${getDateTimeToFrenchText(offerStartDate, options)}`,
      `au ${getDateTimeToFrenchText(offerEndDate, options)}`,
    ]
  }

  return (
    <div className={styles['offer-date']}>
      {getFormattedDatesForOffer(offer).map((date) => (
        <span key={date} data-testid="offer-event-date">
          {date}
        </span>
      ))}
    </div>
  )
}
