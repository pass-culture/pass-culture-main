import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import {
  DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  MAX_OFFERS_TO_DISPLAY,
} from 'core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { hasCollectiveSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { SortingMode } from 'hooks/useColumnSorting'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import { CollectiveOffersSortingColumn } from 'screens/CollectiveOffersScreen/CollectiveOffersScreen'
import { NoResults } from 'screens/IndividualOffersScreen/NoResults/NoResults'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './CollectiveOffersTable.module.scss'
import { CollectiveOffersTableBody } from './CollectiveOffersTableBody/CollectiveOffersTableBody'
import { CollectiveOffersTableHead } from './CollectiveOffersTableHead/CollectiveOffersTableHead'

type CollectiveOffersTableProps = {
  areAllOffersSelected: boolean
  hasOffers: boolean
  isLoading: boolean
  resetFilters: () => void
  setSelectedOffer: (offer: CollectiveOfferResponseModel) => void
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: CollectiveSearchFiltersParams
  isAtLeastOneOfferChecked: boolean
  isRestrictedAsAdmin?: boolean
  selectedOffers: CollectiveOfferResponseModel[]
  offers: CollectiveOfferResponseModel[]
  onColumnHeaderClick: (
    headersName: CollectiveOffersSortingColumn
  ) => SortingMode
  currentSortingColumn: CollectiveOffersSortingColumn | null
  currentSortingMode: SortingMode
  currentPageItems: CollectiveOfferResponseModel[]
}

export const CollectiveOffersTable = ({
  areAllOffersSelected,
  hasOffers,
  isLoading,
  resetFilters,
  selectedOffers,
  setSelectedOffer,
  toggleSelectAllCheckboxes,
  urlSearchFilters,
  isAtLeastOneOfferChecked,
  isRestrictedAsAdmin = false,
  offers,
  onColumnHeaderClick,
  currentSortingColumn,
  currentSortingMode,
  currentPageItems,
}: CollectiveOffersTableProps) => {
  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const defaultCollectiveFilters = isNewOffersAndBookingsActive
    ? DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS
    : DEFAULT_COLLECTIVE_SEARCH_FILTERS

  return (
    <div>
      <div role="status">
        {offers.length > MAX_OFFERS_TO_DISPLAY && (
          <Callout
            variant={CalloutVariant.INFO}
            className={styles['max-display-callout']}
          >
            L’affichage est limité à 500 offres. Modifiez les filtres pour
            affiner votre recherche.
          </Callout>
        )}
        {hasOffers ? (
          `${getOffersCountToDisplay(offers.length)} ${
            offers.length <= 1 ? 'offre' : 'offres'
          }`
        ) : (
          <span className="visually-hidden">aucune offre trouvée</span>
        )}
      </div>
      {isLoading ? (
        <Spinner className={styles['loading-spinner']} />
      ) : (
        <>
          {hasOffers && (
            <>
              <div className={styles['select-all-container']}>
                <BaseCheckbox
                  checked={areAllOffersSelected}
                  partialCheck={
                    !areAllOffersSelected && isAtLeastOneOfferChecked
                  }
                  disabled={isRestrictedAsAdmin}
                  onChange={toggleSelectAllCheckboxes}
                  label={
                    areAllOffersSelected ? (
                      <span className={styles['select-all-container-label']}>
                        Tout désélectionner
                      </span>
                    ) : (
                      <span className={styles['select-all-container-label']}>
                        Tout sélectionner
                      </span>
                    )
                  }
                />
              </div>
              <table className={styles['collective-table']}>
                <CollectiveOffersTableHead
                  onColumnHeaderClick={onColumnHeaderClick}
                  currentSortingColumn={currentSortingColumn}
                  currentSortingMode={currentSortingMode}
                />

                <CollectiveOffersTableBody
                  offers={currentPageItems}
                  selectOffer={setSelectedOffer}
                  selectedOffers={selectedOffers}
                  urlSearchFilters={urlSearchFilters}
                />
              </table>
            </>
          )}
          {!hasOffers &&
            hasCollectiveSearchFilters(
              urlSearchFilters,
              defaultCollectiveFilters
            ) && <NoResults resetFilters={resetFilters} />}
        </>
      )}
    </div>
  )
}
