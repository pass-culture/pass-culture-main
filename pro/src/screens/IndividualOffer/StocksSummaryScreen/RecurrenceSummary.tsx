import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import StocksEventList from 'components/StocksEventList'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'

import { EventCancellationBanner } from '../StocksEventEdition/EventCancellationBanner'

interface RecurrenceSummaryProps {
  offer: GetIndividualOfferResponseModel
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
          priceCategories={offer.priceCategories}
          departmentCode={offer.venue.departementCode}
          offer={offer}
          readonly
        />
      )}
    </>
  )
}
