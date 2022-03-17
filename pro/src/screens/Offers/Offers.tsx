import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import ActionsBarPortal from 'components/layout/ActionsBarPortal/ActionsBarPortal'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import ActionsBarContainer from 'components/pages/Offers/Offers/ActionsBar/ActionsBarContainer'
import NoOffers from 'components/pages/Offers/Offers/NoOffers/NoOffers'
import OffersContainer from 'components/pages/Offers/Offers/OffersContainer'
import { DEFAULT_SEARCH_FILTERS, NUMBER_OF_OFFERS_PER_PAGE } from 'core/Offers'
import { Offer, Offerer, SearchFilters } from 'core/Offers/types'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

import OfferListFilterTabs from './OfferListFilterTabs'

const isAudienceIndividualOrCollective = (
  audience?: string
): audience is 'individual' | 'collective' =>
  audience === 'individual' || audience === 'collective'

interface IOffersProps {
  currentPageNumber: number
  currentUser: { isAdmin: boolean }
  isLoading: boolean
  loadAndUpdateOffers: (filters: SearchFilters) => Promise<void>
  offerer: Offerer | null
  offers: Offer[]
  offersCount: number
  pageCount: number | null
  searchFilters: SearchFilters
  setIsLoading: (isLoading: boolean) => void
  setIsRefreshingOffers: (isRefreshing: boolean) => void
  setOfferer: (offerer: Offerer | null) => void
  setSearchFilters: (searchFilters: SearchFilters) => void
  urlSearchFilters: SearchFilters
  separateIndividualAndCollectiveOffers: boolean
}

const Offers = ({
  currentPageNumber,
  currentUser,
  isLoading,
  loadAndUpdateOffers,
  offerer,
  offers,
  offersCount,
  pageCount,
  searchFilters,
  setIsLoading,
  setIsRefreshingOffers,
  setOfferer,
  setSearchFilters,
  urlSearchFilters,
  separateIndividualAndCollectiveOffers,
}: IOffersProps): JSX.Element => {
  const { audience } = searchFilters
  const [areAllOffersSelected, setAreAllOffersSelected] = useState(false)
  const [selectedOfferIds, setSelectedOfferIds] = useState<string[]>([])
  const [selectedAudience, setSelectedAudience] = useState<
    'individual' | 'collective'
  >(isAudienceIndividualOrCollective(audience) ? audience : 'individual')

  const { isAdmin } = currentUser || {}
  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )
  const hasOffers = currentPageOffersSubset.length > 0
  const hasSearchFilters = useCallback(
    (
      searchFilters: SearchFilters,
      filterNames: (keyof SearchFilters)[] = Object.keys(
        searchFilters
      ) as (keyof SearchFilters)[]
    ) => {
      return filterNames
        .map(
          filterName =>
            searchFilters[filterName] !==
            { ...DEFAULT_SEARCH_FILTERS }[filterName]
        )
        .includes(true)
    },
    []
  )

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasSearchFilters(searchFilters)

  const actionLink =
    userHasNoOffers || isAdmin ? null : (
      <Link className="primary-button with-icon" to="/offre/creation">
        <AddOfferSvg />
        Créer une offre
      </Link>
    )

  const nbSelectedOffers = areAllOffersSelected
    ? offersCount
    : selectedOfferIds.length

  const clearSelectedOfferIds = useCallback(() => {
    setSelectedOfferIds([])
  }, [])

  const refreshOffers = useCallback(
    () => loadAndUpdateOffers(urlSearchFilters),
    [loadAndUpdateOffers, urlSearchFilters]
  )

  const toggleSelectAllCheckboxes = useCallback(() => {
    setAreAllOffersSelected(currentValue => !currentValue)
  }, [])

  const resetFilters = useCallback(() => {
    setIsLoading(true)
    setOfferer(null)
    setSearchFilters({ ...DEFAULT_SEARCH_FILTERS })
  }, [setSearchFilters, setIsLoading, setOfferer])

  return (
    <div className="offers-page">
      <PageTitle title="Vos offres" />
      <Titles action={actionLink} title="Offres" />
      {separateIndividualAndCollectiveOffers && (
        <OfferListFilterTabs
          selectedAudience={selectedAudience}
          setSelectedAudience={setSelectedAudience}
        />
      )}
      <ActionsBarPortal isVisible={nbSelectedOffers > 0}>
        <ActionsBarContainer
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOfferIds}
          nbSelectedOffers={nbSelectedOffers}
          refreshOffers={refreshOffers}
          selectedOfferIds={selectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
        />
      </ActionsBarPortal>
      {userHasNoOffers ? (
        <NoOffers />
      ) : (
        <>
          <h3 className="op-title">Rechercher une offre</h3>
          {hasSearchFilters(searchFilters) ? (
            <Link
              className="reset-filters-link"
              onClick={resetFilters}
              to="/offres"
            >
              Réinitialiser les filtres
            </Link>
          ) : (
            <span className="reset-filters-link disabled">
              Réinitialiser les filtres
            </span>
          )}
        </>
      )}
      <OffersContainer
        areAllOffersSelected={areAllOffersSelected}
        currentPageNumber={currentPageNumber}
        currentPageOffersSubset={currentPageOffersSubset}
        currentUser={currentUser}
        hasOffers={hasOffers}
        hasSearchFilters={hasSearchFilters}
        isLoading={isLoading}
        offerer={offerer}
        offersCount={offersCount}
        pageCount={pageCount}
        refreshOffers={refreshOffers}
        resetFilters={resetFilters}
        searchFilters={searchFilters}
        selectedOfferIds={selectedOfferIds}
        setIsLoading={setIsLoading}
        setIsRefreshingOffers={setIsRefreshingOffers}
        setOfferer={setOfferer}
        setSearchFilters={setSearchFilters}
        setSelectedOfferIds={setSelectedOfferIds}
        toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
        urlSearchFilters={urlSearchFilters}
      />
    </div>
  )
}

export default Offers
