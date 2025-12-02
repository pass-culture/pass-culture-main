import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_OFFER_OPENING_HOURS_QUERY_KEY,
  GET_VENUE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferTimetableScreen } from './components/IndividualOfferTimetableScreen'

export const IndividualOfferTimetable = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()

  const isOhoFFEnabled = useActiveFeature('WIP_ENABLE_OHO')

  const shouldFetchOpeningHoursAndVenue = isOhoFFEnabled

  const {
    isLoading: isOpeningHoursLoading,
    isValidating: isOpeningHoursValidating,
    data: openingHoursData,
  } = useSWR(
    () =>
      offer?.id && shouldFetchOpeningHoursAndVenue
        ? [GET_OFFER_OPENING_HOURS_QUERY_KEY, offer.id]
        : null,
    ([_, offerId]) => api.getOfferOpeningHours(offerId)
  )

  const venueQuery = useSWR(
    offer?.venue.id && shouldFetchOpeningHoursAndVenue
      ? [GET_VENUE_QUERY_KEY, offer.venue.id]
      : null,
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )

  if (
    offer === null ||
    !offer.priceCategories ||
    isOpeningHoursLoading ||
    isOpeningHoursValidating ||
    venueQuery.isLoading
  ) {
    return <Spinner />
  }

  if (!offer.isEvent) {
    navigate('/404')
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <IndividualOfferTimetableScreen
        offer={offer}
        mode={mode}
        openingHours={openingHoursData?.openingHours}
        venue={venueQuery.data}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferTimetable
