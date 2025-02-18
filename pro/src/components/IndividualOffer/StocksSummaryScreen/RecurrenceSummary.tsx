import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import {
  StocksEvent,
  StocksEventList,
} from 'components/StocksEventList/StocksEventList'

import { EventCancellationBanner } from '../StocksEventEdition/EventCancellationBanner'
import { getDepartmentCode } from '../utils/getDepartmentCode'

interface RecurrenceSummaryProps {
  offer: GetIndividualOfferWithAddressResponseModel
  stocks: StocksEvent[]
}

export const RecurrenceSummary = ({
  offer,
  stocks,
}: RecurrenceSummaryProps) => {
  const departmentCode = getDepartmentCode(offer)
  return (
    <>
      <EventCancellationBanner offer={offer} />

      {stocks.length !== 0 && offer.priceCategories && (
        <StocksEventList
          priceCategories={offer.priceCategories}
          departmentCode={departmentCode}
          offer={offer}
          readonly
        />
      )}
    </>
  )
}
