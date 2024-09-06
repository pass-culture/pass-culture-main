import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import {
  StocksEventList,
  StocksEvent,
} from 'components/StocksEventList/StocksEventList'
import { useActiveFeature } from 'hooks/useActiveFeature'

import { EventCancellationBanner } from '../StocksEventEdition/EventCancellationBanner'

interface RecurrenceSummaryProps {
  offer: GetIndividualOfferWithAddressResponseModel
  stocks: StocksEvent[]
}

export const RecurrenceSummary = ({
  offer,
  stocks,
}: RecurrenceSummaryProps) => {
  const useOffererAddressAsDataSourceEnabled = useActiveFeature(
    'WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE'
  )

  const departmentCode = useOffererAddressAsDataSourceEnabled
    ? (offer.address?.departmentCode ?? '')
    : offer.venue.departementCode
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
