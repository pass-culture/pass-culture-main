import React from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { GET_OFFERER_NAMES_QUERY_KEY } from 'config/swrQueryKeys'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { useNotification } from 'hooks/useNotification'
import { OffererStatsScreen } from 'screens/OffererStats/OffererStatsScreen'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

export const OffererStats = (): JSX.Element | null => {
  const notify = useNotification()
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const { data, error, isLoading } = useSWR(
    isNewInterfaceActive ? null : [GET_OFFERER_NAMES_QUERY_KEY],
    () => api.listOfferersNames(),
    {
      fallbackData: { offerersNames: [] },
    }
  )

  if (error) {
    notify.error(error.message)
    return null
  }

  if (!isNewInterfaceActive && !isLoading && data.offerersNames.length === 0) {
    notify.error(GET_DATA_ERROR_MESSAGE)
    return null
  }

  const offererOptions: SelectOption[] = []
  if (isNewInterfaceActive) {
    offererOptions.push({
      value: selectedOffererId?.toString() ?? '',
      label: '',
    })
  } else {
    offererOptions.push(
      ...sortByLabel(
        data.offerersNames.map((offerer) => ({
          value: offerer.id.toString(),
          label: offerer.name,
        }))
      )
    )
  }

  return (
    <AppLayout>
      {!isNewInterfaceActive && isLoading ? (
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
