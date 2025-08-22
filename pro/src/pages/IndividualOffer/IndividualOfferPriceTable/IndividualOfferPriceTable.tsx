import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_STOCKS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferPriceTableScreen } from './components/IndividualOfferPriceTableScreen'

export const IndividualOfferPriceTable = () => {
  const mode = useOfferWizardMode()
  const { offer, offerId } = useIndividualOfferContext()
  assertOrFrontendError(offerId, '`offerId` is undefined.')

  const offerStocksQuery = useSWR([GET_STOCKS_QUERY_KEY, offerId], () =>
    api.getStocks(offerId)
  )

  // TODO (igabriele, 2025-08-20): Handle API error.s
  if (!offer || offerStocksQuery.isLoading || !offerStocksQuery.data) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={`${getTitle(mode)} NEW`}
      mode={mode}
    >
      <IndividualOfferPriceTableScreen
        offer={offer}
        offerStocks={offerStocksQuery.data.stocks}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferPriceTable
