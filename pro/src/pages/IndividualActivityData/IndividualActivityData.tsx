import { useCallback, useEffect, useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { PreFilters } from '@/components/Bookings/Components/PreFilters/PreFilters'
import { downloadIndividualBookingsCSVFile } from '@/components/Bookings/Components/PreFilters/utils/downloadIndividualBookingsCSVFile'
import { downloadIndividualBookingsXLSFile } from '@/components/Bookings/Components/PreFilters/utils/downloadIndividualBookingsXLSFile'
import { useBookingsFilters } from '@/components/Bookings/Components/useBookingsFilters'

import styles from './IndividualActivityData.module.scss'

const IndividualActivityData = () => {
  const { logEvent } = useAnalytics()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const snackBar = useSnackBar()
  const [isDownloading, setIsDownloading] = useState(false)

  const {
    applyNow,
    hasPreFilters,
    isRefreshRequired,
    resetPreFilters,
    selectedPreFilters,
    updateSelectedFilters,
    updateUrl,
    urlParams,
    wereBookingsRequested,
  } = useBookingsFilters()

  // we want to reset filters when selected offerer changes
  // biome-ignore lint/correctness/useExhaustiveDependencies: reset filters when selected offerer changes
  useEffect(() => {
    resetPreFilters()
  }, [resetPreFilters, selectedAdminOfferer.id])

  const resetPreFiltersAndLog = () => {
    resetPreFilters()
    logEvent(Events.CLICKED_RESET_FILTERS)
  }

  const download = useCallback(
    async (type: 'CSV' | 'XLS') => {
      setIsDownloading(true)

      const filters = { ...selectedPreFilters, page: 1 }

      try {
        /* istanbul ignore next: DEBT to fix */
        if (type === 'CSV') {
          await downloadIndividualBookingsCSVFile(
            filters,
            selectedAdminOfferer.id
          )
        } else {
          await downloadIndividualBookingsXLSFile(
            filters,
            selectedAdminOfferer.id
          )
        }
      } catch {
        snackBar.error(GET_DATA_ERROR_MESSAGE)
      }

      setIsDownloading(false)
    },
    [selectedPreFilters, snackBar, selectedAdminOfferer.id]
  )

  return (
    <>
      <h2 className={styles['subtitle']}>
        Téléchargement des réservations individuelles
      </h2>

      <PreFilters
        applyNow={applyNow}
        hasPreFilters={hasPreFilters}
        hasResult={false}
        isAdministrationSpace
        isLocalLoading={false}
        isRefreshRequired={isRefreshRequired}
        isTableLoading={false}
        resetPreFilters={resetPreFiltersAndLog}
        selectedPreFilters={selectedPreFilters}
        updateSelectedFilters={updateSelectedFilters}
        updateUrl={updateUrl}
        urlParams={urlParams}
        wereBookingsRequested={wereBookingsRequested}
        download={download}
        isDownloading={isDownloading}
      />
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualActivityData
