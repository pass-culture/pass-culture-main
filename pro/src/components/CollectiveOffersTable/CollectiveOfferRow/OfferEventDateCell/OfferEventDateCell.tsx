import classNames from 'classnames'

import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  ListOffersVenueResponseModel,
} from '@/apiClient/v1'
import { isCollectiveOfferBookable } from '@/commons/core/OfferEducational/types'
import {
  formatShortDateForInput,
  getDateTimeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'

import styles from '../Cells.module.scss'

export interface OfferEventDateCellProps {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
  rowId: string
  className?: string
}

function getOfferDate(
  date: string,
  isTemplate: boolean,
  venue: ListOffersVenueResponseModel
) {
  return isTemplate
    ? toDateStrippedOfTimezone(date)
    : getLocalDepartementDateTimeFromUtc(date, venue.departementCode)
}

export const OfferEventDateCell = ({
  rowId,
  offer,
  className,
}: OfferEventDateCellProps) => {
  const isTemplateTable = !isCollectiveOfferBookable(offer)

  const getFormattedDatesForOffer = (
    offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
  ) => {
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
    const offerStartDate = getOfferDate(
      offerDatetimes.start,
      isTemplateTable,
      offer.venue
    )
    const offerEndDate = getOfferDate(
      offerDatetimes.end,
      isTemplateTable,
      offer.venue
    )
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
    <td
      // biome-ignore lint/a11y: accepted for assistive technologies
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['event-date-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().EVENT_DATE.id}`}
    >
      <div className={styles['offer-event']}>
        {getFormattedDatesForOffer(offer).map((date) => (
          <span key={date} data-testid="offer-event-date">
            {date}
          </span>
        ))}
      </div>
    </td>
  )
}
