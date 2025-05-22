import { useRef, useState } from 'react'

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
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { isSameOffer } from 'commons/utils/isSameOffer'
import { NoData } from 'components/NoData/NoData'
import { useStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'

import { IndividualOffersActionsBar } from './components/IndividualOffersActionsBar/IndividualOffersActionsBar'
import { IndividualOffersSearchFilters } from './components/IndividualOffersSearchFilters/IndividualOffersSearchFilters'
import { HeadlineOffer } from './components/IndividualOffersTable/components/HeadlineOffer/HeadlineOffer'
import { IndividualOffersTable } from './components/IndividualOffersTable/IndividualOffersTable'

export type IndividualOffersContainerProps = {
  currentPageNumber: number
  isLoading: boolean
  initialSearchFilters: SearchFiltersParams
  redirectWithSelectedFilters: (
    filters: Partial<SearchFiltersParams> & {
      page?: number
      audience?: Audience
    }
  ) => void
  offererAddresses: SelectOption[]
  categories?: SelectOption[]
  offers?: ListOffersOfferResponseModel[]
}

export const IndividualOffersContainer = ({
  currentPageNumber,
  isLoading,
  initialSearchFilters,
  redirectWithSelectedFilters,
  offererAddresses,
  categories,
  offers = [],
}: IndividualOffersContainerProps): JSX.Element => {
  const { onApplyFilters, onResetFilters } = useStoredFilterConfig('individual')
  const [selectedOffers, setSelectedOffers] = useState<
    ListOffersOfferResponseModel[]
  >([])
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)
  const isCollapsedMemorizedFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )

  const searchButtonRef = useRef<HTMLButtonElement>(null)

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const hasFilters = hasSearchFilters({
    searchFilters: initialSearchFilters,
    ignore: ['nameOrIsbn'],
  })
  const hasFiltersOrNameSearch = hasFilters || !!initialSearchFilters.nameOrIsbn

  const userHasNoOffers = !isLoading && !hasOffers && !hasFiltersOrNameSearch

  const areAllOffersSelected =
    selectedOffers.length > 0 && selectedOffers.length === offers.length

  function clearSelectedOffers() {
    setSelectedOffers([])
  }

  function toggleSelectAllCheckboxes() {
    setSelectedOffers(areAllOffersSelected ? [] : offers)
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const applySelectedFiltersAndRedirect = (
    filters: Partial<SearchFiltersParams> & { audience?: Audience }
  ) => {
    redirectWithSelectedFilters(filters)
  }

  const applyFilters = (filters: SearchFiltersParams) => {
    onApplyFilters(filters)
    applySelectedFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  const resetFilters = (resetNameOrIsbn = true) => {
    onResetFilters(resetNameOrIsbn)
    const newFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...(!resetNameOrIsbn && { nameOrIsbn: initialSearchFilters.nameOrIsbn }),
    }
    setSelectedFilters(newFilters)
    applySelectedFiltersAndRedirect(newFilters)
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
      <IndividualOffersSearchFilters
        hasFilters={hasFilters}
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        resetFilters={() => resetFilters(!isCollapsedMemorizedFiltersEnabled)}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        offererAddresses={offererAddresses}
        searchButtonRef={searchButtonRef}
      />
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <>
          <HeadlineOffer />
          <IndividualOffersTable
            applySelectedFiltersAndRedirect={applySelectedFiltersAndRedirect}
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
            hasFiltersOrNameSearch={hasFiltersOrNameSearch}
            selectedFilters={selectedFilters}
            isAtLeastOneOfferChecked={selectedOffers.length > 1}
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
                searchButtonRef={searchButtonRef}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
