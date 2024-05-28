import React from 'react'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { GET_OFFERER_NAMES_QUERY_KEY } from 'config/swrQueryKeys'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import useNotification from 'hooks/useNotification'
import { OffererStatsScreen } from 'screens/OffererStats/OffererStatsScreen'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

export const OffererStats = (): JSX.Element | null => {
  const notify = useNotification()
  const { data, error, isLoading } = useSWR(
    [GET_OFFERER_NAMES_QUERY_KEY],
    () => api.listOfferersNames(),
    {
      fallbackData: { offerersNames: [] },
    }
  )

  if (error) {
    notify.error(error.message)
    return null
  }

  if (data.offerersNames.length === 0) {
    notify.error(GET_DATA_ERROR_MESSAGE)
    return null
  }

  const offererOptions = sortByLabel(
    data.offerersNames.map((offerer) => ({
      value: offerer.id.toString(),
      label: offerer.name,
    }))
  )

  return (
    <AppLayout>
      {isLoading ? (
        <Spinner />
      ) : (
        <OffererStatsScreen offererOptions={offererOptions} />
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OffererStats
