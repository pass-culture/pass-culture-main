import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { StatisticsModel } from '@/apiClient/v1'
import { GET_STATISTICS_QUERY_KEY } from '@/commons/config/swrQueryKeys'

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
    hasIncomeData,
    years,
  }
}
