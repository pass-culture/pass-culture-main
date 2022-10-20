import { getValue } from '@firebase/remote-config'
import React from 'react'

import Spinner from 'components/layout/Spinner'
import { useGetOffererNames } from 'core/Offerers/adapters'
import useNotification from 'hooks/useNotification'
import useRemoteConfig from 'hooks/useRemoteConfig'
import { OffererStatsScreen } from 'screens/OffererStats'
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
  const { remoteConfig } = useRemoteConfig()

  const biggest500 =
    remoteConfig &&
    getValue(remoteConfig, 'only500BiggerActors').asString().split(',')

  const offererOptions = sortByDisplayName(
    offererNames
      .filter(offerer => biggest500?.includes(offerer.id))
      .map(offerer => ({
        id: offerer.id,
        displayName: offerer.name,
      }))
  )
  return offererOptions.length > 0 ? (
    <OffererStatsScreen offererOptions={offererOptions} />
  ) : null
}

export default OffererStats
