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
  const { offer, hasPublishedOfferWithSameEan } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

  const {
    isLoading: isOpeningHoursLoading,
    isValidating: isOpeningHoursValidating,
    data: openingHoursData,
  } = useSWR(
    () => (!offer?.id ? null : [GET_OFFER_OPENING_HOURS_QUERY_KEY, offer.id]),
    ([_, offerId]) => api.getOfferOpeningHours(offerId)
  )

  const { isLoading: isStocksLoading, data: stocksData } = useSWR(
    !offer?.id ? null : [GET_STOCKS_QUERY_KEY, offer.id],
    ([, offerId]) => api.getStocks(offerId)
  )

  if (
    offer === null ||
    !offer.priceCategories ||
    isOpeningHoursLoading ||
    isOpeningHoursValidating ||
    isStocksLoading ||
    !stocksData
  ) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={hasPublishedOfferWithSameEan}
    >
      <IndividualOfferTimetableScreen
        offer={offer}
        mode={mode}
        openingHours={openingHoursData?.openingHours}
        stocks={stocksData.stocks}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferTimetable
