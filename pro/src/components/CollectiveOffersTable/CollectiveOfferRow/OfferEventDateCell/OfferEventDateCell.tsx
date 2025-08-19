import classNames from 'classnames'

import type {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
} from '@/apiClient/v1'
import {
  getDateTimeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'
import styles from '@/styles/components/Cells.module.scss'

export interface OfferEventDateCellProps {
  offer: CollectiveOfferResponseModel
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
  function formattedTime(hour: string | null | undefined) {
    if (!hour) {
      return
    }
    const offerStartDatetime = getOfferDate(hour, offer.isShowcase, offer.venue)

    const timeFormatter = new Intl.DateTimeFormat('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
    })

    const formattedTime = timeFormatter
      .format(offerStartDatetime)
      .replace(':', 'h')

    return formattedTime
  }

  const getFormattedDatesForOffer = (offer: CollectiveOfferResponseModel) => {
    const offerDates = offer.dates

    const options: Intl.DateTimeFormatOptions = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }

    if (!offerDates?.start || !offerDates.end) {
      return ['Toute l’année scolaire']
    }
    if (offerDates.start === offerDates.end) {
      return [
        `${getDateTimeToFrenchText(
          getOfferDate(offerDates.start, offer.isShowcase, offer.venue),
          options
        )}`,
      ]
    }

    return [
      `Du ${getDateTimeToFrenchText(getOfferDate(offerDates.start, offer.isShowcase, offer.venue), options)}`,
      `au ${getDateTimeToFrenchText(getOfferDate(offerDates.end, offer.isShowcase, offer.venue), options)}`,
    ]
  }

  return (
    <td
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
        {!offer.isShowcase && (
          <span className={styles['offer-event-hours']}>
            {formattedTime(offer.dates?.start)}
          </span>
        )}
      </div>
    </td>
  )
}
