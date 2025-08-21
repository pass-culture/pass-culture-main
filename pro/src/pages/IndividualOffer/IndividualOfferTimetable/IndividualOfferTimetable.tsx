import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_OFFER_OPENING_HOURS_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferTimetableScreen } from './components/IndividualOfferTimetableScreen'

export const IndividualOfferTimetable = (): JSX.Element | null => {
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

  const offerOpeningHoursQuery = useSWR(
    () => (!offer?.id ? null : [GET_OFFER_OPENING_HOURS_QUERY_KEY, offer.id]),
    ([_, offerId]) => api.getOfferOpeningHours(offerId)
  )

  const stocksQuery = useSWR(
    !offer?.id ? null : [GET_STOCKS_QUERY_KEY, offer.id],
    ([, offerId]) => api.getStocks(offerId)
  )

  if (
    offer === null ||
    !offer.priceCategories ||
    offerOpeningHoursQuery.isLoading ||
    stocksQuery.isLoading
  ) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      <IndividualOfferTimetableScreen
        offer={offer}
        mode={mode}
        openingHours={offerOpeningHoursQuery.data?.openingHours}
        stocks={stocksQuery.data?.stocks}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferTimetable
