import React, { useCallback, useEffect, useState } from 'react'

import { UserRole } from 'apiClient/v1'
import NoOffers from 'components/NoData'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
  OFFER_STATUS_DRAFT,
} from 'core/Offers/constants'
import { Offer, Offerer, SearchFiltersParams } from 'core/Offers/types'
import {
  computeCollectiveOffersUrl,
  computeOffersUrl,
  hasSearchFilters,
} from 'core/Offers/utils'
import { Audience } from 'core/shared'
import getUserValidatedOfferersNamesAdapter from 'core/shared/adapters/getUserValidatedOfferersNamesAdapter'
import { SelectOption } from 'custom_types/form'
import fullPlusIcon from 'icons/full-plus.svg'
import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import ActionsBar from 'pages/Offers/Offers/ActionsBar'
import OffersContainer from 'pages/Offers/Offers/Offers'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Tabs from 'ui-kit/Tabs'
import Titles from 'ui-kit/Titles/Titles'

import SearchFilters from './SearchFilters'

export interface OffersProps {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  loadAndUpdateOffers: (filters: SearchFiltersParams) => Promise<void>
  offerer: Offerer | null
  offers: Offer[]
  setOfferer: (offerer: Offerer | null) => void
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
  categories: SelectOption[]
}

const Offers = ({
  currentPageNumber,
  currentUser,
  isLoading,
  loadAndUpdateOffers,
  offerer,
  offers,
  setOfferer,
  initialSearchFilters,
  audience,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  categories,
}: OffersProps): JSX.Element => {
  const [searchFilters, setSearchFilters] =
    useState<SearchFiltersParams>(initialSearchFilters)
  const [isRefreshingOffers, setIsRefreshingOffers] = useState(true)

  const [areAllOffersSelected, setAreAllOffersSelected] = useState(false)
  const [selectedOfferIds, setSelectedOfferIds] = useState<string[]>([])

  const { isAdmin } = currentUser
  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )
  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasSearchFilters(urlSearchFilters)

  const hasDifferentFiltersFromLastSearch = useCallback(
    (
      searchFilters: SearchFiltersParams,
      filterNames: (keyof SearchFiltersParams)[] = Object.keys(
        searchFilters
      ) as (keyof SearchFiltersParams)[]
    ) => {
      const lastSearchFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...urlSearchFilters,
      }
      return filterNames
        .map(
          (filterName) =>
            searchFilters[filterName] !== lastSearchFilters[filterName]
        )
        .includes(true)
    },
    [urlSearchFilters]
  )

  const [isOffererValidated, setIsOffererValidated] = useState<boolean>(false)

  useEffect(() => {
    const loadValidatedUserOfferers = async () => {
      const validatedUserOfferers = await getUserValidatedOfferersNamesAdapter()
      if (
        validatedUserOfferers.isOk &&
        validatedUserOfferers?.payload?.length
      ) {
        setIsOffererValidated(true)
      } else {
        setIsOffererValidated(false)
      }
    }
    // If user is admin, offer creation button doesn't show
    if (!isAdmin) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadValidatedUserOfferers()
    }
  }, [])

  const actionLink =
    isAdmin || !isOffererValidated ? undefined : (
      <ButtonLink
        variant={ButtonVariant.PRIMARY}
        link={{ isExternal: false, to: '/offre/creation' }}
        icon={fullPlusIcon}
      >
        Créer une offre
      </ButtonLink>
    )

  const nbSelectedOffers = areAllOffersSelected
    ? offers.length
    : selectedOfferIds.length

  const clearSelectedOfferIds = useCallback(() => {
    /* istanbul ignore next: DEBT, TO FIX */
    setSelectedOfferIds([])
  }, [])

  const refreshOffers = useCallback(
    () => loadAndUpdateOffers(initialSearchFilters),
    [loadAndUpdateOffers, initialSearchFilters]
  )

  const toggleSelectAllCheckboxes = useCallback(() => {
    setAreAllOffersSelected((currentValue) => !currentValue)
  }, [])

  const resetFilters = () => {
    setOfferer(null)
    setSearchFilters(DEFAULT_SEARCH_FILTERS)
    applyUrlFiltersAndRedirect(DEFAULT_SEARCH_FILTERS)
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  useEffect(() => {
    if (isRefreshingOffers) {
      setSearchFilters(initialSearchFilters)
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadAndUpdateOffers(initialSearchFilters)
    }
  }, [
    isRefreshingOffers,
    loadAndUpdateOffers,
    setSearchFilters,
    initialSearchFilters,
  ])

  const applyUrlFiltersAndRedirect = (
    filters: SearchFiltersParams & { audience?: Audience },
    isRefreshing = true
  ) => {
    setIsRefreshingOffers(isRefreshing)
    redirectWithUrlFilters(filters)
  }

  const applyFilters = async () => {
    // FIXME : this code's part seems to be useless
    if (!hasDifferentFiltersFromLastSearch(searchFilters)) {
      await refreshOffers()
    }
    applyUrlFiltersAndRedirect({ ...searchFilters, page: DEFAULT_PAGE })
  }

  const removeOfferer = () => {
    setOfferer(null)
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

  const getUpdateOffersStatusMessage = (tmpSelectedOfferIds: string[]) => {
    const selectedOffers = offers.filter((offer) =>
      tmpSelectedOfferIds.includes(offer.id.toString())
    )
    if (selectedOffers.some((offer) => offer.status === OFFER_STATUS_DRAFT)) {
      return 'Vous ne pouvez pas publier des brouillons depuis cette liste'
    }
    if (
      audience == Audience.COLLECTIVE &&
      selectedOffers.some((offer) => offer.hasBookingLimitDatetimesPassed)
    ) {
      return 'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
    }
    return ''
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const canDeleteOffers = (tmpSelectedOfferIds: string[]) => {
    const selectedOffers = offers.filter((offer) =>
      tmpSelectedOfferIds.includes(offer.id.toString())
    )
    return !selectedOffers.some((offer) => offer.status !== OFFER_STATUS_DRAFT)
  }
  return (
    <div className="offers-page">
      <Titles action={actionLink} title="Offres" />
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
        <NoOffers audience={audience} page="offers" />
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
          refreshOffers={refreshOffers}
          isAtLeastOneOfferChecked={selectedOfferIds.length > 0}
        />
      )}
      {nbSelectedOffers > 0 && (
        <ActionsBar
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOfferIds}
          nbSelectedOffers={nbSelectedOffers}
          refreshOffers={refreshOffers}
          selectedOfferIds={selectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
          audience={audience}
          getUpdateOffersStatusMessage={getUpdateOffersStatusMessage}
          canDeleteOffers={canDeleteOffers}
        />
      )}
    </div>
  )
}

export default Offers
