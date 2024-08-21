import { useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
  GetOffererResponseModel,
  UserRole,
} from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { NoData } from 'components/NoData/NoData'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { hasCollectiveSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { SelectOption } from 'custom_types/form'
import { CollectiveOffersActionsBar } from 'pages/Offers/OffersTable/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { CollectiveOffersTable } from 'pages/Offers/OffersTable/CollectiveOffersTable/CollectiveOffersTable'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'
import { Titles } from 'ui-kit/Titles/Titles'

import styles from './CollectiveOffersScreen.module.scss'
import { CollectiveOffersSearchFilters } from './CollectiveOffersSearchFilters/CollectiveOffersSearchFilters'

export type CollectiveOffersScreenProps = {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  offerer: GetOffererResponseModel | null
  initialSearchFilters: CollectiveSearchFiltersParams
  redirectWithUrlFilters: (
    filters: CollectiveSearchFiltersParams & {
      page?: number
    }
  ) => void
  urlSearchFilters: CollectiveSearchFiltersParams
  venues: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
  offers: CollectiveOfferResponseModel[]
}

export const CollectiveOffersScreen = ({
  currentPageNumber,
  isLoading,
  offerer,
  initialSearchFilters,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  categories,
  isRestrictedAsAdmin,
  offers,
}: CollectiveOffersScreenProps): JSX.Element => {
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasCollectiveSearchFilters(urlSearchFilters)

  const areAllOffersSelected =
    selectedOffers.length > 0 &&
    selectedOffers.length === offers.filter((offer) => offer.isEditable).length

  function clearSelectedOfferIds() {
    setSelectedOffers([])
  }

  function toggleSelectAllCheckboxes() {
    setSelectedOffers(
      areAllOffersSelected ? [] : offers.filter((offer) => offer.isEditable)
    )
  }

  const resetFilters = () => {
    setSelectedFilters(DEFAULT_COLLECTIVE_SEARCH_FILTERS)
    applyUrlFiltersAndRedirect({
      ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    })
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const applyUrlFiltersAndRedirect = (
    filters: CollectiveSearchFiltersParams
  ) => {
    redirectWithUrlFilters(filters)
  }

  const applyFilters = (filters: CollectiveSearchFiltersParams) => {
    applyUrlFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  const removeOfferer = () => {
    const updatedFilters = {
      ...initialSearchFilters,
      offererId: DEFAULT_COLLECTIVE_SEARCH_FILTERS.offererId,
    }
    if (
      initialSearchFilters.venueId ===
        DEFAULT_COLLECTIVE_SEARCH_FILTERS.venueId &&
      initialSearchFilters.status !== DEFAULT_COLLECTIVE_SEARCH_FILTERS.status
    ) {
      updatedFilters.status = DEFAULT_COLLECTIVE_SEARCH_FILTERS.status
    }
    applyUrlFiltersAndRedirect(updatedFilters)
  }

  const getUpdateOffersStatusMessage = (tmpSelectedOfferIds: number[]) => {
    const selectedOffers = offers.filter((offer) =>
      tmpSelectedOfferIds.includes(offer.id)
    )
    if (
      selectedOffers.some(
        (offer) => offer.status === CollectiveOfferStatus.DRAFT
      )
    ) {
      return 'Vous ne pouvez pas publier des brouillons depuis cette liste'
    }
    if (selectedOffers.some((offer) => offer.hasBookingLimitDatetimesPassed)) {
      return 'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
    }
    return ''
  }

  function onSetSelectedOffer(offer: CollectiveOfferResponseModel) {
    const matchingOffer = selectedOffers.find((selectedOffer) =>
      isSameOffer(offer, selectedOffer)
    )

    if (matchingOffer) {
      setSelectedOffers((offers) =>
        offers.filter((collectiveOffer) => collectiveOffer !== matchingOffer)
      )
    } else {
      setSelectedOffers((selectedOffers) => {
        return [...selectedOffers, offer]
      })
    }
  }

  return (
    <div>
      <Titles title="Offres collectives" />
      <CollectiveOffersSearchFilters
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        removeOfferer={removeOfferer}
        resetFilters={resetFilters}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        venues={venues}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />

      <Callout
        className={styles['banner']}
        variant={CalloutVariant.INFO}
        links={[
          {
            href: 'https://aide.passculture.app/hc/fr/articles/4416082284945--Acteurs-Culturels-Quel-est-le-cycle-de-vie-de-votre-offre-collective-de-sa-cr%C3%A9ation-%C3%A0-son-remboursement',
            label: 'En savoir plus sur les statuts',
            isExternal: true,
          },
        ]}
      >
        <div className={styles['banner-onboarding']}>
          <span className={styles['banner-onboarding-title']}>
            C’est nouveau ! Vous pouvez désormais archiver vos offres
            collectives.
          </span>
          <span>
            Cliquez sur le bouton “Actions” pour archiver vos offres. Elles ne
            seront plus visibles sur ADAGE. Vous pourrez les retrouver en
            filtrant sur le statut “Archivée”.{' '}
          </span>
        </div>
      </Callout>
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <>
          <CollectiveOffersTable
            applyUrlFiltersAndRedirect={applyUrlFiltersAndRedirect}
            areAllOffersSelected={areAllOffersSelected}
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
            offers={offers}
          />
          <div role="status">
            {selectedOffers.length > 0 && (
              <CollectiveOffersActionsBar
                areAllOffersSelected={areAllOffersSelected}
                clearSelectedOfferIds={clearSelectedOfferIds}
                selectedOffers={selectedOffers}
                toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
                getUpdateOffersStatusMessage={getUpdateOffersStatusMessage}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
