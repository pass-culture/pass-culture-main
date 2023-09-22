import StocksEventList from 'components/StocksEventList'
import { IndividualOffer } from 'core/Offers/types'

import { getInitialStocks } from '../StocksEventCreation/StocksEventCreation'
import { EventCancellationBanner } from '../StocksEventEdition/EventCancellationBanner'

interface RecurrenceSummaryProps {
  offer: IndividualOffer
}

export const RecurrenceSummary = ({ offer }: RecurrenceSummaryProps) => {
  const stocks = getInitialStocks(offer)

  return (
    <>
      <EventCancellationBanner offer={offer} />

      {stocks.length !== 0 && offer?.priceCategories && (
        <StocksEventList
          stocks={stocks}
          priceCategories={offer.priceCategories}
          departmentCode={offer.venue.departmentCode}
          offerId={offer.id}
          readonly
        />
      )}
    </>
  )
}
