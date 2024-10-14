import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import {
  StocksEventList,
  StocksEvent,
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
  const useOffererAddressAsDataSourceEnabled = useActiveFeature(
    'WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE'
  )

  const departmentCode = getDepartmentCode({
    offer,
    useOffererAddressAsDataSourceEnabled,
  })
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
