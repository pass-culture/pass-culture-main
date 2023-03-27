import React from 'react'

import { useGetOffererNames } from 'core/Offerers/adapters'
import useNotification from 'hooks/useNotification'
import { OffererStatsScreen } from 'screens/OffererStats'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByDisplayName } from 'utils/strings'

const OffererStats = (): JSX.Element | null => {
  const notify = useNotification()
  const { isLoading, error, data: offererNames } = useGetOffererNames({})
  if (isLoading) {
    return <Spinner />
  }
  if (error) {
    notify.error(error.message)
    return null
  }

  const offererOptions = sortByDisplayName(
    offererNames.map(offerer => ({
      id: offerer.nonHumanizedId.toString(),
      displayName: offerer.name,
    }))
  )
  return <OffererStatsScreen offererOptions={offererOptions} />
}

export default OffererStats
