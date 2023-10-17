import StocksEventList from 'components/StocksEventList'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { IndividualOffer } from 'core/Offers/types'

import { EventCancellationBanner } from '../StocksEventEdition/EventCancellationBanner'

interface RecurrenceSummaryProps {
  offer: IndividualOffer
  stocks: StocksEvent[]
}

export const RecurrenceSummary = ({
  offer,
  stocks,
}: RecurrenceSummaryProps) => {
  return (
    <>
      <EventCancellationBanner offer={offer} />

      {stocks.length !== 0 && offer?.priceCategories && (
        <StocksEventList
          stocks={stocks}
          priceCategories={offer.priceCategories}
          departmentCode={offer.venue.departementCode}
          offerId={offer.id}
          readonly
        />
      )}
    </>
  )
}
