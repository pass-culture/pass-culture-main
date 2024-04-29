import React from 'react'

import { AppLayout } from 'app/AppLayout'
import useGetOffererNames from 'core/Offerers/adapters/getOffererNamesAdapter/useOffererNames'
import useNotification from 'hooks/useNotification'
import { OffererStatsScreen } from 'screens/OffererStats'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

export const OffererStats = (): JSX.Element | null => {
  const notify = useNotification()
  const { isLoading, error, data: offererNames } = useGetOffererNames({})

  if (error) {
    notify.error(error.message)
    return null
  }

  const offererOptions = sortByLabel(
    offererNames?.map((offerer) => ({
      value: offerer.id.toString(),
      label: offerer.name,
    })) ?? []
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
