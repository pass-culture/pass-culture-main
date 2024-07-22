import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { getDateTimeToFrenchText } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import styles from '../../OfferRow.module.scss'

export interface OfferEventDateCellProps {
  offer: CollectiveOfferResponseModel
}

export const OfferEventDateCell = ({ offer }: OfferEventDateCellProps) => {
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
    if (offer.stocks.length === 0) {
      return []
    }

    const offerStock = offer.stocks[0]!

    const options: Intl.DateTimeFormatOptions = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }

    if (!offerStock.startDatetime || !offerStock.endDatetime) {
      return ['Toute l’année scolaire']
    }
    if (offerStock.startDatetime === offerStock.endDatetime) {
      return [
        `${getDateTimeToFrenchText(
          getLocalDepartementDateTimeFromUtc(
            offerStock.startDatetime,
            offer.venue.departementCode
          ),
          options
        )}`,
      ]
    }

    return [
      `du ${getDateTimeToFrenchText(new Date(offerStock.startDatetime), options)}`,
      `au ${getDateTimeToFrenchText(new Date(offerStock.endDatetime), options)}`,
    ]
  }

  return (
    <td>
      <div className={styles['offer-event']}>
        {getFormattedDatesForOffer(offer).map((date) => (
          <span key={date}>{date}</span>
        ))}
        {offer.stocks.length > 0 && (
          <span className={styles['offer-event-hours']}>
            à partir de {formattedTime(offer.stocks[0]!.startDatetime)}
          </span>
        )}
      </div>
    </td>
  )
}
