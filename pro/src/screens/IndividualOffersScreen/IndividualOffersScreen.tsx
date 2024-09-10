import { useState } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  ListOffersOfferResponseModel,
  OfferStatus,
  UserRole,
} from 'apiClient/v1'
import { NoData } from 'components/NoData/NoData'
import { GET_VALIDATED_OFFERERS_NAMES_QUERY_KEY } from 'config/swrQueryKeys'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
  OFFER_STATUS_DRAFT,
} from 'core/Offers/constants'
import {
  CollectiveSearchFiltersParams,
  SearchFiltersParams,
} from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils/computeCollectiveOffersUrl'
import { computeIndividualOffersUrl } from 'core/Offers/utils/computeIndividualOffersUrl'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { Audience } from 'core/shared/types'
import { SelectOption } from 'custom_types/form'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullPlusIcon from 'icons/full-plus.svg'
import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { IndividualOffersActionsBar } from 'pages/Offers/OffersTable/IndividualOffersTable/IndividualOffersActionsBar/IndividualOffersActionsBar'
import { IndividualOffersTable } from 'pages/Offers/OffersTable/IndividualOffersTable/IndividualOffersTable'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'
import { selectCurrentOffererId } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Tabs } from 'ui-kit/Tabs/Tabs'

import styles from './IndividualOffersScreen.module.scss'
import { IndividualOffersSearchFilters } from './IndividualOffersSearchFilters/IndividualOffersSearchFilters'

export type IndividualOffersScreenProps = {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  offerer: GetOffererResponseModel | null
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

export const IndividualOffersScreen = ({
  currentPageNumber,
  currentUser,
  isLoading,
  offerer,
  initialSearchFilters,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  offererAddresses,
  categories,
  isRestrictedAsAdmin,
  offers = [],
}: IndividualOffersScreenProps): JSX.Element => {
  const [selectedOffers, setSelectedOffers] = useState<
    ListOffersOfferResponseModel[]
  >([])
  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const { isAdmin } = currentUser

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasSearchFilters(urlSearchFilters)

  const validatedUserOfferersQuery = useSWR(
    !isAdmin ? [GET_VALIDATED_OFFERERS_NAMES_QUERY_KEY] : null,
    () => api.listOfferersNames(undefined, true)
  )

  const isOffererValidated =
    validatedUserOfferersQuery.data?.offerersNames.some(
      (validatedOfferer) => validatedOfferer.id === selectedOffererId
    )
  const displayCreateOfferButton =
    !isNewSideBarNavigation && !isAdmin && isOffererValidated

  const areAllOffersSelected =
    selectedOffers.length > 0 && selectedOffers.length === offers.length

  function clearSelectedOfferIds() {
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

  const removeOfferer = () => {
    const updatedFilters = {
      ...initialSearchFilters,
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
    }
    if (
      initialSearchFilters.venueId === DEFAULT_SEARCH_FILTERS.venueId &&
      initialSearchFilters.status !== DEFAULT_SEARCH_FILTERS.status
    ) {
      updatedFilters.status = DEFAULT_SEARCH_FILTERS.status
    }
    applyUrlFiltersAndRedirect(updatedFilters)
  }

  const getUpdateOffersStatusMessage = (tmpSelectedOfferIds: number[]) => {
    const selectedOffers = offers.filter((offer) =>
      tmpSelectedOfferIds.includes(offer.id)
    )
    if (selectedOffers.some((offer) => offer.status === OFFER_STATUS_DRAFT)) {
      return 'Vous ne pouvez pas publier des brouillons depuis cette liste'
    }
    return ''
  }

  const canDeleteOffers = selectedOffers.some(
    (offer) => offer.status === OfferStatus.DRAFT
  )

  const isNewInterfaceActive = useIsNewInterfaceActive()
  const title = isNewInterfaceActive ? 'Offres individuelles' : 'Offres'

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

  return (
    <div>
      <div className={styles['title-container']}>
        <h1 className={styles['title']}>{title}</h1>
        {displayCreateOfferButton && (
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to={`/offre/creation${selectedOffererId ? `?structure=${selectedOffererId}` : ''}`}
            icon={fullPlusIcon}
          >
            Créer une offre
          </ButtonLink>
        )}
      </div>
      {!isNewSideBarNavigation && (
        <Tabs
          nav="Offres individuelles et collectives"
          selectedKey={Audience.INDIVIDUAL}
          tabs={[
            {
              label: 'Offres individuelles',
              url: computeIndividualOffersUrl({
                ...initialSearchFilters,
                status: DEFAULT_SEARCH_FILTERS.status,
                page: currentPageNumber,
              }),
              key: 'individual',
              icon: strokeUserIcon,
            },
            {
              label: 'Offres collectives',
              url: computeCollectiveOffersUrl({
                ...initialSearchFilters,
                status: DEFAULT_COLLECTIVE_SEARCH_FILTERS.status,
                page: currentPageNumber,
              } as CollectiveSearchFiltersParams),
              key: 'collective',
              icon: strokeLibraryIcon,
            },
          ]}
        />
      )}
      <IndividualOffersSearchFilters
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        removeOfferer={removeOfferer}
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
                clearSelectedOfferIds={clearSelectedOfferIds}
                selectedOfferIds={selectedOffers.map((offer) => offer.id)}
                toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
                getUpdateOffersStatusMessage={getUpdateOffersStatusMessage}
                canDeleteOffers={canDeleteOffers}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
