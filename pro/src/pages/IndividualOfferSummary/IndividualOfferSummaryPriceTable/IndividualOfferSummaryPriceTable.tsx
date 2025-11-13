import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_STOCKS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferSummaryPriceTableScreen } from './components/IndividualOfferSummaryPriceTableScreen'

export const IndividualOfferSummaryPriceTable = (): JSX.Element | null => {
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
      <IndividualOfferSummaryPriceTableScreen
        offer={offer}
        offerStocks={getStocksQuery.data?.stocks ?? []}
      />
      <ActionBar
        isDisabled={false}
        step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryPriceTable
