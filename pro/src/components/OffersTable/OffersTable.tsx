import { MAX_OFFERS_TO_DISPLAY } from 'commons/core/Offers/constants'
import { getOffersCountToDisplay } from 'commons/utils/getOffersCountToDisplay'
import { NoResults } from 'components/NoResults/NoResults'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { Callout } from 'ui-kit/Callout/Callout'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './OffersTable.module.scss'

type OffersTableProps = {
  hasOffers: boolean
  hasFiltersOrNameSearch: boolean
  offersCount: number
  isLoading: boolean
  resetFilters: () => void
  children: React.ReactNode
  pagination?: React.ReactNode
  areAllOffersSelected: boolean
  isAtLeastOneOfferChecked: boolean
  toggleSelectAllCheckboxes: () => void
}

export const OffersTable = ({
  hasOffers,
  hasFiltersOrNameSearch,
  offersCount,
  isLoading,
  resetFilters,
  children,
  pagination,
  areAllOffersSelected,
  isAtLeastOneOfferChecked,
  toggleSelectAllCheckboxes,
}: OffersTableProps) => {
  const isSelectAllIndeterminate =
    !areAllOffersSelected && isAtLeastOneOfferChecked

  return (
    <>
      <div role="status">
        {offersCount > MAX_OFFERS_TO_DISPLAY && (
          <Callout className={styles['offers-table-callout']}>
            L’affichage est limité à {MAX_OFFERS_TO_DISPLAY} offres. Modifiez
            les filtres pour affiner votre recherche.
          </Callout>
        )}
        {hasOffers && (
          <div className={styles['offers-table-title']}>
            <h2
              id="offers-table-title"
              className={styles['offers-table-title-heading']}
            >
              Liste des offres
            </h2>
            <div>
              {`${getOffersCountToDisplay(offersCount)} ${
                offersCount <= 1 ? 'offre' : 'offres'
              }`}
            </div>
          </div>
        )}
      </div>
      {isLoading ? (
        <Spinner className={styles['offers-table-spinner']} />
      ) : (
        <>
          {hasOffers && (
            <>
              <div className={styles['select-all-checkbox']}>
                <Checkbox
                  checked={areAllOffersSelected}
                  indeterminate={isSelectAllIndeterminate}
                  onChange={toggleSelectAllCheckboxes}
                  label={
                    areAllOffersSelected
                      ? 'Tout désélectionner'
                      : 'Tout sélectionner'
                  }
                />
              </div>
              <table
                role="table"
                className={styles['offers-table-table']}
                aria-labelledby="offers-table-title"
              >
                {children}
              </table>
              {pagination && (
                <div className={styles['offers-table-pagination']}>
                  {pagination}
                </div>
              )}
            </>
          )}
          {!hasOffers && hasFiltersOrNameSearch && (
            <NoResults resetFilters={resetFilters} />
          )}
        </>
      )}
    </>
  )
}
