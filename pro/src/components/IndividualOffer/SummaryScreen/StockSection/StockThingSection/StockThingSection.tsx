import { format } from 'date-fns-tz'

import { GetOfferStockResponseModel } from 'apiClient/v1'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'commons/utils/date'
import { formatPrice } from 'commons/utils/formatPrice'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'

interface StockThingSectionProps {
  stock?: GetOfferStockResponseModel
  canBeDuo?: boolean
  isDuo: boolean
}

export const StockThingSection = ({
  stock,
  canBeDuo,
  isDuo,
}: StockThingSectionProps) => {
  if (!stock) {
    return null
  }

  const descriptions = []
  descriptions.push({ title: 'Prix', text: formatPrice(stock.price) })
  if (stock.bookingLimitDatetime) {
    descriptions.push({
      title: 'Date limite de réservation',
      text: format(
        toDateStrippedOfTimezone(stock.bookingLimitDatetime),
        FORMAT_DD_MM_YYYY
      ),
    })
  }
  descriptions.push({
    title: 'Quantité',
    text:
      stock.quantity !== null && stock.quantity !== undefined
        ? new Intl.NumberFormat('fr-FR').format(stock.quantity)
        : 'Illimité',
  })
  {
    /* Some things offer can be duo like ESCAPE_GAME or CARTE_MUSEE */
  }
  if (canBeDuo) {
    descriptions.push({
      title: 'Accepter les réservations "Duo"',
      text: isDuo ? 'Oui' : 'Non',
    })
  }

  return <SummaryDescriptionList descriptions={descriptions} />
}
