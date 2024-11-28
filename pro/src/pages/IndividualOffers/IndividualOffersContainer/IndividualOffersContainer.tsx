import { useState } from 'react'

import { ListOffersOfferResponseModel, OfferStatus } from 'apiClient/v1'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { hasSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { Audience } from 'commons/core/shared/types'
import { SelectOption } from 'commons/custom_types/form'
import { isSameOffer } from 'commons/utils/isSameOffer'
import { NoData } from 'components/NoData/NoData'

import { IndividualOffersActionsBar } from './components/IndividualOffersActionsBar/IndividualOffersActionsBar'
import { IndividualOffersSearchFilters } from './components/IndividualOffersSearchFilters/IndividualOffersSearchFilters'
import { IndividualOffersTable } from './components/IndividualOffersTable/IndividualOffersTable'
import styles from './IndividualOffersContainer.module.scss'

export type IndividualOffersContainerProps = {
  currentPageNumber: number
  isLoading: boolean
  initialSearchFilters: SearchFiltersParams
  redirectWithUrlFilters: (
    filters: SearchFiltersParams & {
      page?: number
      audience?: Audience
    }
  ) => void
  urlSearchFilters: SearchFiltersParams
  venues: SelectOption[]
  offererAddresses: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
  offers?: ListOffersOfferResponseModel[]
}

export const IndividualOffersContainer = ({
  currentPageNumber,
  isLoading,
  initialSearchFilters,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  offererAddresses,
  categories,
  isRestrictedAsAdmin,
  offers = [],
}: IndividualOffersContainerProps): JSX.Element => {
  const [selectedOffers, setSelectedOffers] = useState<
    ListOffersOfferResponseModel[]
  >([])
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasSearchFilters(urlSearchFilters)

  const areAllOffersSelected =
    selectedOffers.length > 0 && selectedOffers.length === offers.length

  function clearSelectedOffers() {
    setSelectedOffers([])
  }

  function toggleSelectAllCheckboxes() {
    setSelectedOffers(areAllOffersSelected ? [] : offers)
  }

  const resetFilters = () => {
    setSelectedFilters(DEFAULT_SEARCH_FILTERS)
    applyUrlFiltersAndRedirect({
      ...DEFAULT_SEARCH_FILTERS,
    })
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const applyUrlFiltersAndRedirect = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    redirectWithUrlFilters(filters)
  }

  const applyFilters = (filters: SearchFiltersParams) => {
    applyUrlFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  function onSetSelectedOffer(offer: ListOffersOfferResponseModel) {
    const matchingOffer = selectedOffers.find((selectedOffer) =>
      isSameOffer(offer, selectedOffer)
    )

    if (matchingOffer) {
      setSelectedOffers((offers) =>
        offers.filter((indivOffer) => indivOffer !== matchingOffer)
      )
    } else {
      setSelectedOffers((selectedOffers) => {
        return [...selectedOffers, offer]
      })
    }
  }
  const canDelete = selectedOffers.some(
    (offer) => offer.status === OfferStatus.DRAFT
  )
  const canPublish = selectedOffers.some(
    (offer) => offer.status === OfferStatus.INACTIVE
  )
  const canDeactivate = selectedOffers.some(
    (offer) =>
      offer.status === OfferStatus.ACTIVE ||
      offer.status === OfferStatus.EXPIRED ||
      offer.status === OfferStatus.SOLD_OUT
  )
  return (
    <div>
      <div className={styles['title-container']}>
        <h1 className={styles['title']}>Offres individuelles</h1>
      </div>
      <IndividualOffersSearchFilters
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        resetFilters={resetFilters}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        venues={venues}
        offererAddresses={offererAddresses}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <>
          <IndividualOffersTable
            applyUrlFiltersAndRedirect={applyUrlFiltersAndRedirect}
            areAllOffersSelected={areAllOffersSelected}
            currentPageNumber={currentPageNumber}
            currentPageOffersSubset={currentPageOffersSubset}
            hasOffers={hasOffers}
            isLoading={isLoading}
            offersCount={offers.length}
            pageCount={pageCount}
            resetFilters={resetFilters}
            selectedOffers={selectedOffers}
            setSelectedOffer={onSetSelectedOffer}
            toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
            urlSearchFilters={urlSearchFilters}
            isAtLeastOneOfferChecked={selectedOffers.length > 1}
            isRestrictedAsAdmin={isRestrictedAsAdmin}
          />
          <div role="status">
            {selectedOffers.length > 0 && (
              <IndividualOffersActionsBar
                areAllOffersSelected={areAllOffersSelected}
                clearSelectedOffers={clearSelectedOffers}
                selectedOffers={selectedOffers.map((offer) => ({
                  id: offer.id,
                  status: offer.status,
                }))}
                toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
                canDelete={canDelete}
                canDeactivate={canDeactivate}
                canPublish={canPublish}
                isRestrictedAsAdmin={Boolean(isRestrictedAsAdmin)}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
