import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { getDateTimeToFrenchText } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import styles from '../Cells.module.scss'

export interface OfferEventDateCellProps {
  offer: CollectiveOfferResponseModel
  headers?: string
}

export const OfferEventDateCell = ({
  offer,
  headers,
}: OfferEventDateCellProps) => {
  function formattedTime(hour: string | null | undefined) {
    if (!hour) {
      return
    }

    const offerStartDatetime = new Date(hour)

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
          getLocalDepartementDateTimeFromUtc(
            offerDates.start,
            offer.venue.departementCode
          ),
          options
        )}`,
      ]
    }

    return [
      `du ${getDateTimeToFrenchText(new Date(offerDates.start), options)}`,
      `au ${getDateTimeToFrenchText(new Date(offerDates.end), options)}`,
    ]
  }

  return (
    <td headers={headers} className={styles['offers-table-cell']}>
      <div className={styles['offer-event']}>
        {getFormattedDatesForOffer(offer).map((date) => (
          <span key={date}>{date}</span>
        ))}
        <span className={styles['offer-event-hours']}>
          {formattedTime(offer.dates?.start)}
        </span>
      </div>
    </td>
  )
}
