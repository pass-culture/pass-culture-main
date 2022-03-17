import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { Link, useHistory } from 'react-router-dom'

import ActionsBarPortal from 'components/layout/ActionsBarPortal/ActionsBarPortal'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'
import { Banner } from 'ui-kit'

import { computeOffersUrl } from '../utils/computeOffersUrl'

import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from './_constants'
import ActionsBarContainer from './ActionsBar/ActionsBarContainer'
import NoOffers from './NoOffers/NoOffers'
import NoResults from './NoResults/NoResults'
import OffersTableBody from './OffersTableBody/OffersTableBody'
import OffersTableHead from './OffersTableHead/OffersTableHead'
import SearchFilters from './SearchFilters/SearchFilters'

const Offers = ({ currentUser, getOfferer }) => {
  const dispatch = useDispatch()
  const history = useHistory()
  const [urlSearchFilters, urlPageNumber] = useQuerySearchFilters()

  useEffect(() => {
    setCurrentPageNumber(urlPageNumber)
    dispatch(
      saveSearchFilters({
        nameOrIsbn:
          urlSearchFilters.nameOrIsbn || DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        offererId:
          urlSearchFilters.offererId || DEFAULT_SEARCH_FILTERS.offererId,
        venueId: urlSearchFilters.venueId || DEFAULT_SEARCH_FILTERS.venueId,
        categoryId:
          urlSearchFilters.categoryId || DEFAULT_SEARCH_FILTERS.categoryId,
        status: urlSearchFilters.status
          ? urlSearchFilters.status
          : DEFAULT_SEARCH_FILTERS.status,
        creationMode: urlSearchFilters.creationMode
          ? urlSearchFilters.creationMode
          : DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate:
          urlSearchFilters.periodBeginningDate ||
          DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate:
          urlSearchFilters.periodEndingDate ||
          DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    )
    dispatch(savePageNumber(urlPageNumber))
  }, [dispatch, urlPageNumber, urlSearchFilters])
  const [isLoading, setIsLoading] = useState(true)
  const [offersCount, setOffersCount] = useState(0)
  const [currentPageNumber, setCurrentPageNumber] = useState(DEFAULT_PAGE)
  const [pageCount, setPageCount] = useState(null)
  const [searchFilters, setSearchFilters] = useState({
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  })
  const [offerer, setOfferer] = useState(null)
  const [isStatusFiltersVisible, setIsStatusFiltersVisible] = useState(false)
  const [areAllOffersSelected, setAreAllOffersSelected] = useState(false)

  const [offers, setOffers] = useState([])
  const [selectedOfferIds, setSelectedOfferIds] = useState([])
  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )
  const [isRefreshingOffers, setIsRefreshingOffers] = useState(true)

  const applyUrlFiltersAndRedirect = useCallback(
    (filters, isRefreshing = true) => {
      setIsRefreshingOffers(isRefreshing)
      const newUrl = computeOffersUrl(filters, filters.page)

      history.push(newUrl)
    },
    [history]
  )

  useEffect(() => {
    if (
      urlSearchFilters.offererId &&
      urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
    ) {
      getOfferer(urlSearchFilters.offererId).then(offerer =>
        setOfferer(offerer)
      )
    }
  }, [getOfferer, urlSearchFilters.offererId])

  useEffect(() => {
    if (currentUser.isAdmin) {
      const isVenueFilterSelected =
        searchFilters.venueId !== DEFAULT_SEARCH_FILTERS.venueId
      const isOffererFilterApplied =
        urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
      const isFilterByVenueOrOfferer =
        isVenueFilterSelected || isOffererFilterApplied

      if (!isFilterByVenueOrOfferer) {
        setSearchFilters(currentSearchFilters => ({
          ...currentSearchFilters,
          status: DEFAULT_SEARCH_FILTERS.status,
        }))
      }
    }
  }, [currentUser.isAdmin, urlSearchFilters.offererId, searchFilters.venueId])

  const loadAndUpdateOffers = useCallback(filters => {
    const apiFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...filters,
    }
    pcapi
      .loadFilteredOffers(apiFilters)
      .then(offers => {
        const offersCount = offers.length
        setIsLoading(false)
        setOffersCount(offersCount)
        const pageCount = Math.ceil(offersCount / NUMBER_OF_OFFERS_PER_PAGE)
        const cappedPageCount = Math.min(pageCount, MAX_TOTAL_PAGES)
        setPageCount(cappedPageCount)
        setOffers(offers)
      })
      .catch(() => setIsLoading(false))
  }, [])

  const refreshOffers = useCallback(
    () => loadAndUpdateOffers(urlSearchFilters),
    [loadAndUpdateOffers, urlSearchFilters]
  )
  const hasDifferentFiltersFromLastSearch = useCallback(
    (searchFilters, filterNames = Object.keys(searchFilters)) => {
      const lastSearchFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...urlSearchFilters,
      }
      return filterNames
        .map(
          filterName =>
            searchFilters[filterName] !== lastSearchFilters[filterName]
        )
        .includes(true)
    },
    [urlSearchFilters]
  )
  const applyFilters = useCallback(() => {
    setIsLoading(true)
    setIsStatusFiltersVisible(false)

    if (!hasDifferentFiltersFromLastSearch(searchFilters)) {
      refreshOffers()
    }
    applyUrlFiltersAndRedirect(searchFilters)
  }, [
    hasDifferentFiltersFromLastSearch,
    refreshOffers,
    searchFilters,
    applyUrlFiltersAndRedirect,
  ])

  useEffect(() => {
    if (isRefreshingOffers) {
      setSearchFilters(urlSearchFilters)
      loadAndUpdateOffers(urlSearchFilters)
    }
  }, [
    isRefreshingOffers,
    loadAndUpdateOffers,
    setSearchFilters,
    urlSearchFilters,
  ])

  const removeOfferer = useCallback(() => {
    setIsLoading(true)
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
  }, [applyUrlFiltersAndRedirect, searchFilters])

  const hasSearchFilters = useCallback(
    (searchFilters, filterNames = Object.keys(searchFilters)) => {
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

  const isAdminForbidden = useCallback(
    searchFilters => {
      return (
        currentUser.isAdmin &&
        !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
      )
    },
    [currentUser.isAdmin, hasSearchFilters]
  )

  const updateStatusFilter = useCallback(selectedStatus => {
    setSearchFilters(currentSearchFilters => ({
      ...currentSearchFilters,
      status: selectedStatus,
    }))
  }, [])

  const onPreviousPageClick = useCallback(() => {
    const newPageNumber = currentPageNumber - 1
    applyUrlFiltersAndRedirect(
      { ...urlSearchFilters, ...{ page: newPageNumber } },
      false
    )
  }, [currentPageNumber, applyUrlFiltersAndRedirect, urlSearchFilters])

  const onNextPageClick = useCallback(() => {
    const newPageNumber = currentPageNumber + 1
    applyUrlFiltersAndRedirect(
      { ...urlSearchFilters, ...{ page: newPageNumber } },
      false
    )
  }, [currentPageNumber, applyUrlFiltersAndRedirect, urlSearchFilters])

  const selectOffer = useCallback((offerId, selected) => {
    setSelectedOfferIds(currentSelectedIds => {
      let newSelectedOfferIds = [...currentSelectedIds]
      if (selected) {
        newSelectedOfferIds.push(offerId)
      } else {
        const offerIdIndex = newSelectedOfferIds.indexOf(offerId)
        newSelectedOfferIds.splice(offerIdIndex, 1)
      }
      return newSelectedOfferIds
    })
  }, [])

  const toggleSelectAllCheckboxes = useCallback(() => {
    setAreAllOffersSelected(currentValue => !currentValue)
  }, [])

  function selectAllOffers() {
    setSelectedOfferIds(
      areAllOffersSelected
        ? []
        : currentPageOffersSubset
            .filter(offer => !isOfferDisabled(offer.status))
            .map(offer => offer.id)
    )

    toggleSelectAllCheckboxes()
  }

  const clearSelectedOfferIds = useCallback(() => {
    setSelectedOfferIds([])
  }, [])

  const resetFilters = useCallback(() => {
    setIsLoading(true)
    setOfferer(null)
    setSearchFilters({ ...DEFAULT_SEARCH_FILTERS })
  }, [setSearchFilters])

  const { isAdmin } = currentUser || {}
  const hasOffers = currentPageOffersSubset.length > 0
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

  const isLastPage = currentPageNumber === pageCount

  return (
    <div className="offers-page">
      <PageTitle title="Vos offres" />
      <Titles action={actionLink} title="Offres" />
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

          <SearchFilters
            applyFilters={applyFilters}
            offerer={offerer}
            removeOfferer={removeOfferer}
            selectedFilters={searchFilters}
            setSearchFilters={setSearchFilters}
          />

          <div aria-busy={isLoading} aria-live="polite" className="section">
            {isLoading ? (
              <Spinner />
            ) : (
              <>
                {offersCount > MAX_OFFERS_TO_DISPLAY && (
                  <Banner type="notification-info">
                    L’affichage est limité à 500 offres. Modifiez les filtres
                    pour affiner votre recherche.
                  </Banner>
                )}
                {hasOffers && (
                  <div className="offers-count">
                    {`${getOffersCountToDisplay(offersCount)} ${
                      offersCount <= 1 ? 'offre' : 'offres'
                    }`}
                  </div>
                )}
                <table>
                  <OffersTableHead
                    applyFilters={applyFilters}
                    areAllOffersSelected={areAllOffersSelected}
                    areOffersPresent={hasOffers}
                    filters={searchFilters}
                    isAdminForbidden={isAdminForbidden}
                    isStatusFiltersVisible={isStatusFiltersVisible}
                    selectAllOffers={selectAllOffers}
                    setIsStatusFiltersVisible={setIsStatusFiltersVisible}
                    updateStatusFilter={updateStatusFilter}
                  />
                  <OffersTableBody
                    areAllOffersSelected={areAllOffersSelected}
                    offers={currentPageOffersSubset}
                    selectOffer={selectOffer}
                    selectedOfferIds={selectedOfferIds}
                  />
                </table>
                {hasOffers && (
                  <div className="pagination">
                    <button
                      disabled={currentPageNumber === 1}
                      onClick={onPreviousPageClick}
                      type="button"
                    >
                      <Icon
                        alt="Aller à la page précédente"
                        svg="ico-left-arrow"
                      />
                    </button>
                    <span>{`Page ${currentPageNumber}/${pageCount}`}</span>
                    <button
                      disabled={isLastPage}
                      onClick={onNextPageClick}
                      type="button"
                    >
                      <Icon
                        alt="Aller à la page suivante"
                        svg="ico-right-arrow"
                      />
                    </button>
                  </div>
                )}
                {!hasOffers && hasSearchFilters(urlSearchFilters) && (
                  <NoResults resetFilters={resetFilters} />
                )}
              </>
            )}
          </div>
        </>
      )}
    </div>
  )
}

Offers.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  getOfferer: PropTypes.func.isRequired,
}

export default Offers
