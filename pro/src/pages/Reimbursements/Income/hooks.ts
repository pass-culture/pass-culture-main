import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetOffererResponseModel, StatisticsModel } from 'apiClient/v1'
import {
  GET_OFFERER_QUERY_KEY,
  GET_STATISTICS_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from 'pages/Homepage/components/Offerers/components/VenueList/venueUtils'
import { formatAndOrderVenues } from 'repository/venuesService'

export const useVenues = () => {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const {
    data: selectedOfferer,
    error: venuesApiError,
    isLoading: areVenuesLoading,
  } = useSWR<GetOffererResponseModel | null, string, [string, number] | null>(
    selectedOffererId ? [GET_OFFERER_QUERY_KEY, selectedOffererId] : null,
    ([, offererIdParam]) => api.getOfferer(offererIdParam)
  )

  const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
  const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)
  const rawVenues = [...physicalVenues, virtualVenue].filter((v) => !!v)
  const venues = formatAndOrderVenues(rawVenues)

  const hasVenuesData = venues.length > 0
  const venuesDataReady = !areVenuesLoading && !venuesApiError && hasVenuesData

  return {
    areVenuesLoading,
    venuesApiError,
    venuesDataReady,
    venues,
    selectedOffererId,
  }
}

export const useIncome = (selectedVenues: string[]) => {
  // Sorting venues makes sure passed query keys are always the same
  // so SWR can cache the data correctly.
  const selectedVenuesAsNumbers = selectedVenues.map(Number).sort()
  const {
    data,
    error: incomeApiError,
    isLoading: isIncomeLoading,
  } = useSWR<StatisticsModel | null, string, [string, number[]] | null>(
    selectedVenuesAsNumbers.length > 0
      ? [GET_STATISTICS_QUERY_KEY, selectedVenuesAsNumbers]
      : null,
    ([, selectedVenuesParam]) => api.getStatistics(selectedVenuesParam),
    { revalidateOnMount: true }
  )

  const incomeByYear = data?.incomeByYear
  const hasIncomeData = incomeByYear && Object.keys(incomeByYear).length > 0
  const incomeDataReady = !isIncomeLoading && !incomeApiError && hasIncomeData
  const years = incomeDataReady
    ? Object.keys(incomeByYear)
        .map(Number)
        .sort((a, b) => b - a)
    : []

  return {
    isIncomeLoading,
    incomeApiError,
    incomeDataReady,
    incomeByYear,
    years,
  }
}
