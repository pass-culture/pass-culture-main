import { useState } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
  ListOffersOfferResponseModel,
  UserRole,
} from 'apiClient/v1'
import { NoData } from 'components/NoData/NoData'
import { GET_VALIDATED_OFFERERS_NAMES_QUERY_KEY } from 'config/swrQueryKeys'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
  OFFER_STATUS_DRAFT,
} from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import {
  computeOffersUrl,
  computeCollectiveOffersUrl,
} from 'core/Offers/utils/computeOffersUrl'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { Audience } from 'core/shared/types'
import { SelectOption } from 'custom_types/form'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import fullPlusIcon from 'icons/full-plus.svg'
import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { ActionsBar } from 'pages/Offers/Offers/ActionsBar/ActionsBar'
import OffersContainer from 'pages/Offers/Offers/Offers'
import { selectCurrentOffererId } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Tabs } from 'ui-kit/Tabs/Tabs'
import Titles from 'ui-kit/Titles/Titles'

import { SearchFilters } from './SearchFilters/SearchFilters'

export interface OffersProps {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  offerer: GetOffererResponseModel | null
  offers: CollectiveOfferResponseModel[] | ListOffersOfferResponseModel[]
  initialSearchFilters: SearchFiltersParams
  audience: Audience
  redirectWithUrlFilters: (
    filters: SearchFiltersParams & {
      page?: number
      audience?: Audience
    }
  ) => void
  urlSearchFilters: SearchFiltersParams
  venues: SelectOption[]
  categories?: SelectOption[]
}

export const Offers = ({
  currentPageNumber,
  currentUser,
  isLoading,
  offerer,
  offers,
  initialSearchFilters,
  audience,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  categories,
}: OffersProps): JSX.Element => {
  const [searchFilters, setSearchFilters] =
    useState<SearchFiltersParams>(initialSearchFilters)

  const [selectedOfferIds, setSelectedOfferIds] = useState<number[]>([])
  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)

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

  const actionLink = displayCreateOfferButton ? (
    <ButtonLink
      variant={ButtonVariant.PRIMARY}
      link={{
        isExternal: false,
        to: `/offre/creation${selectedOffererId ? `?structure=${selectedOffererId}` : ''}`,
      }}
      icon={fullPlusIcon}
    >
      Créer une offre
    </ButtonLink>
  ) : undefined

  const selectedOffers = offers.filter((offer) =>
    selectedOfferIds.includes(offer.id)
  )

  const areAllOffersSelected =
    selectedOffers.length ===
    offers.filter((offer) => !isOfferDisabled(offer.status)).length

  function clearSelectedOfferIds() {
    setSelectedOfferIds([])
  }

  function toggleSelectAllCheckboxes() {
    setSelectedOfferIds(
      areAllOffersSelected
        ? []
        : offers
            .filter((offer) => !isOfferDisabled(offer.status))
            .map((offer) => offer.id)
    )
  }

  const resetFilters = () => {
    setSearchFilters(DEFAULT_SEARCH_FILTERS)
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

  const applyFilters = () => {
    applyUrlFiltersAndRedirect({ ...searchFilters, page: DEFAULT_PAGE })
  }

  const removeOfferer = () => {
    const updatedFilters = {
      ...searchFilters,
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
    }
    if (
      searchFilters.venueId === DEFAULT_SEARCH_FILTERS.venueId &&
      searchFilters.status !== DEFAULT_SEARCH_FILTERS.status
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
    if (
      audience === Audience.COLLECTIVE &&
      selectedOffers.some((offer) => offer.hasBookingLimitDatetimesPassed)
    ) {
      return 'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
    }
    return ''
  }

  const canDeleteOffers = () => {
    return selectedOffers.some((offer) => offer.status !== OFFER_STATUS_DRAFT)
  }

  const isNewInterfaceActive = useIsNewInterfaceActive()
  const title = isNewInterfaceActive
    ? audience === Audience.COLLECTIVE
      ? 'Offres collectives'
      : 'Offres individuelles'
    : 'Offres'

  return (
    <div className="offers-page">
      <Titles action={actionLink} title={title} />
      {!isNewSideBarNavigation && (
        <Tabs
          nav="Offres individuelles et collectives"
          selectedKey={audience}
          tabs={[
            {
              label: 'Offres individuelles',
              url: computeOffersUrl({
                ...searchFilters,
                status: DEFAULT_SEARCH_FILTERS.status,
                page: currentPageNumber,
              }),
              key: 'individual',
              icon: strokeUserIcon,
            },
            {
              label: 'Offres collectives',
              url: computeCollectiveOffersUrl({
                ...searchFilters,
                status: DEFAULT_SEARCH_FILTERS.status,
                page: currentPageNumber,
              }),
              key: 'collective',
              icon: strokeLibraryIcon,
            },
          ]}
        />
      )}

      <SearchFilters
        applyFilters={applyFilters}
        audience={audience}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        removeOfferer={removeOfferer}
        resetFilters={resetFilters}
        selectedFilters={searchFilters}
        setSearchFilters={setSearchFilters}
        venues={venues}
      />
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <OffersContainer
          applyFilters={applyFilters}
          applyUrlFiltersAndRedirect={applyUrlFiltersAndRedirect}
          areAllOffersSelected={areAllOffersSelected}
          audience={audience}
          currentPageNumber={currentPageNumber}
          currentPageOffersSubset={currentPageOffersSubset}
          currentUser={currentUser}
          hasOffers={hasOffers}
          isLoading={isLoading}
          offersCount={offers.length}
          pageCount={pageCount}
          resetFilters={resetFilters}
          searchFilters={searchFilters}
          selectedOfferIds={selectedOfferIds}
          setSearchFilters={setSearchFilters}
          setSelectedOfferIds={setSelectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
          urlSearchFilters={urlSearchFilters}
          isAtLeastOneOfferChecked={selectedOfferIds.length > 0}
        />
      )}
      {selectedOfferIds.length > 0 && (
        <ActionsBar
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOfferIds}
          selectedOfferIds={selectedOfferIds}
          selectedOffers={selectedOffers}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
          audience={audience}
          getUpdateOffersStatusMessage={getUpdateOffersStatusMessage}
          canDeleteOffers={canDeleteOffers}
        />
      )}
    </div>
  )
}
