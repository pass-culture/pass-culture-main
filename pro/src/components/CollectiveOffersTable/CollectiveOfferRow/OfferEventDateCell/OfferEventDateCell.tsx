import classNames from 'classnames'
import styles from 'styles/components/Cells.module.scss'

import {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
} from '@/apiClient//v1'
import {
  getDateTimeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'
import { getCellsDefinition } from '@/components/OffersTable/utils/cellDefinitions'

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

    if (
      offer.isShowcase &&
      offerStartDatetime.getHours() === 0 &&
      offerStartDatetime.getMinutes() === 0
    ) {
      //  Template offers may not have a specific hour set. In that case the api created the dates at midnight UTC.
      //  Therefore, template start dates at midnight UTC should not have a time displayed
      return
    }

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
      `du ${getDateTimeToFrenchText(getOfferDate(offerDates.start, offer.isShowcase, offer.venue), options)}`,
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
        <span className={styles['offer-event-hours']}>
          {formattedTime(offer.dates?.start)}
        </span>
      </div>
    </td>
  )
}
