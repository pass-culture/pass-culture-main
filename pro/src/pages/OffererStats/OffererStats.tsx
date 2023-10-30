import React from 'react'

import { useGetOffererNames } from 'core/Offerers/adapters'
import useNotification from 'hooks/useNotification'
import { OffererStatsScreen } from 'screens/OffererStats'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

const OffererStats = (): JSX.Element | null => {
  const notify = useNotification()
  const { isLoading, error, data: offererNames } = useGetOffererNames({})

  if (error) {
    notify.error(error.message)
  }

  return (
    <>
      <Spinner isLoading={isLoading} />
      {!isLoading && !error && (
        <OffererStatsScreen
          offererOptions={sortByLabel(
            offererNames.map((offerer) => ({
              value: offerer.id.toString(),
              label: offerer.name,
            }))
          )}
        />
      )}
    </>
  )
}

export default OffererStats
