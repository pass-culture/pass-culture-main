import { useRef, useState } from 'react'

import { Events } from '@/commons/core/FirebaseEvents/constants'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { hasCollectiveSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { downloadBookableOffersFile } from '@/components/CollectiveOffersTable/utils/downloadBookableOffersFile'
import { DownloadDropdown } from '@/components/DownloadDropdown/DownloadDropdown'

import { CollectiveOffersSearchFilters } from '../CollectiveOffers/components/CollectiveOffersScreen/CollectiveOffersSearchFilters/CollectiveOffersSearchFilters'
import styles from './CollectiveActivityData.module.scss'

const CollectiveActivityData = () => {
  const searchButtonRef = useRef<HTMLButtonElement>(null)

  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const snackBar = useSnackBar()

  const [isDownloading, setIsDownloading] = useState(false)
  const [selectedFilters, setSelectedFilters] = useState(
    DEFAULT_COLLECTIVE_SEARCH_FILTERS
  )

  const selectedFiltersWithOffererId = {
    ...selectedFilters,
    offererId: selectedAdminOfferer.id.toString(),
  }

  const download = async (type: 'CSV' | 'XLS') => {
    setIsDownloading(true)

    try {
      await downloadBookableOffersFile(selectedFiltersWithOffererId, type)
    } catch {
      snackBar.error(GET_DATA_ERROR_MESSAGE)
    }

    setIsDownloading(false)
  }

  const hasFilters = hasCollectiveSearchFilters({
    searchFilters: selectedFilters,
    defaultFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ignore: ['offererId'],
  })

  const resetFilters = () => {
    setSelectedFilters(DEFAULT_COLLECTIVE_SEARCH_FILTERS)
  }

  return (
    <>
      <h2 className={styles['subtitle']}>
        Téléchargement des offres réservables
      </h2>

      <CollectiveOffersSearchFilters
        hasFilters={hasFilters}
        isAdministrationSpace
        offererId={selectedAdminOfferer.id.toString()}
        resetFilters={resetFilters}
        searchButtonRef={searchButtonRef}
        selectedFilters={selectedFiltersWithOffererId}
        setSelectedFilters={setSelectedFilters}
      />

      <DownloadDropdown
        isDisabled={isDownloading}
        label="Télécharger les offres réservables"
        logEventNames={{
          onSelectCsv: Events.CLICKED_DOWNLOAD_COLLECTIVE_OFFERS_CSV,
          onSelectXls: Events.CLICKED_DOWNLOAD_COLLECTIVE_OFFERS_XLS,
          onToggle: Events.CLICKED_DOWNLOAD_COLLECTIVE_OFFERS,
        }}
        onSelect={download}
      />
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveActivityData
