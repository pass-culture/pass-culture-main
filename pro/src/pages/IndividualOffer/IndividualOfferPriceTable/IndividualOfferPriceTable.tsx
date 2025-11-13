import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_STOCKS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferPriceTableScreen } from './components/IndividualOfferPriceTableScreen'

export const IndividualOfferPriceTable = () => {
  const { offer, offerId } = useIndividualOfferContext()
  assertOrFrontendError(offerId, '`offerId` is undefined.')

  const shouldFetchStocks = offer && !offer.isEvent

  const getStocksQuery = useSWR(
    shouldFetchStocks ? [GET_STOCKS_QUERY_KEY, offerId] : null,
    () => api.getStocks(offerId)
  )

  // TODO (igabriele, 2025-08-20): Handle API error.s
  if (!offer || getStocksQuery.isLoading) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferPriceTableScreen
        offer={offer}
        offerStocks={getStocksQuery.data?.stocks}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferPriceTable
