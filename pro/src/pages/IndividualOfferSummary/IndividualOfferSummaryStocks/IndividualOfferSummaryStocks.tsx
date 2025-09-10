/* istanbul ignore file: DEBT, TO FIX */

import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_OFFER_OPENING_HOURS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { areOpeningHoursEmpty } from '@/pages/IndividualOffer/IndividualOfferTimetable/commons/areOpeningHoursEmpty'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferSummaryStocksCalendarScreen } from './components/IndividualOfferSummaryStocksCalendarScreen/IndividualOfferSummaryStocksCalendarScreen'
import { IndividualOfferSummaryStocksScreen } from './components/IndividualOfferSummaryStocksScreen/IndividualOfferSummaryStocksScreen'
import { IndividualOfferSummaryStocksTimetableScreen } from './components/IndividualOfferSummaryStocksTimetableScreen/IndividualOfferSummaryStocksTimetableScreen'

const IndividualOfferSummaryStocks = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const offerOpeningHoursQuery = useSWR(
    () => (!offer?.id ? null : [GET_OFFER_OPENING_HOURS_QUERY_KEY, offer.id]),
    ([_, offerId]) => api.getOfferOpeningHours(offerId)
  )

  const openingHoursEmpty = areOpeningHoursEmpty(
    offerOpeningHoursQuery.data?.openingHours
  )

  if (offer === null) {
    return <Spinner />
  }

  if (isNewOfferCreationFlowFeatureActive) {
    return (
      <IndividualOfferLayout offer={offer}>
        {!offerOpeningHoursQuery.data || openingHoursEmpty ? (
          <IndividualOfferSummaryStocksCalendarScreen offer={offer} />
        ) : (
          <IndividualOfferSummaryStocksTimetableScreen
            offer={offer}
            openingHours={offerOpeningHoursQuery.data.openingHours}
          />
        )}
        <ActionBar
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
          isDisabled={false}
        />
      </IndividualOfferLayout>
    )
  }

  return (
    <IndividualOfferLayout offer={offer}>
      {offer.isEvent ? (
        <IndividualOfferSummaryStocksCalendarScreen offer={offer} />
      ) : (
        <IndividualOfferSummaryStocksScreen />
      )}
      <ActionBar
        step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
        isDisabled={false}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryStocks
