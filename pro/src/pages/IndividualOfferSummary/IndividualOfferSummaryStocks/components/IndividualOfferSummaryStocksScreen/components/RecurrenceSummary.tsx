import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { getDepartmentCode } from 'commons/utils/getDepartmentCode'
import { EventCancellationBanner } from 'components/EventCancellationBanner/EventCancellationBanner'
import {
  StocksEvent,
  StocksEventList,
} from 'components/StocksEventList/StocksEventList'

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
