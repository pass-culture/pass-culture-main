import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import ActionsBarPortal from 'components/layout/ActionsBarPortal/ActionsBarPortal'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import Titles from 'components/layout/Titles/Titles'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import { saveSearchFilters } from 'store/offers/actions'
import { selectOffers } from 'store/offers/selectors'
import { loadOffers } from 'store/offers/thunks'
import { mapApiToBrowser, mapBrowserToApi, translateQueryParamsToApiParams } from 'utils/translate'

import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from './_constants'
import ActionsBarContainer from './ActionsBar/ActionsBarContainer'
import NoOffers from './NoOffers/NoOffers'
import NoResults from './NoResults/NoResults'
import OffersTableBody from './OffersTableBody/OffersTableBody'
import OffersTableHead from './OffersTableHead/OffersTableHead'
import SearchFilters from './SearchFilters/SearchFilters'

const Offers = ({ currentUser, getOfferer, query }) => {
  const dispatch = useDispatch()

  useEffect(() => {
    const searchFiltersInUri = translateQueryParamsToApiParams(query.parse())
    dispatch(
      saveSearchFilters({
        name: searchFiltersInUri.name || DEFAULT_SEARCH_FILTERS.name,
        offererId: searchFiltersInUri.offererId || DEFAULT_SEARCH_FILTERS.offererId,
        venueId: searchFiltersInUri.venueId || DEFAULT_SEARCH_FILTERS.venueId,
        typeId: searchFiltersInUri.typeId || DEFAULT_SEARCH_FILTERS.typeId,
        status: searchFiltersInUri.status
          ? mapBrowserToApi[searchFiltersInUri.status]
          : DEFAULT_SEARCH_FILTERS.status,
        creationMode: searchFiltersInUri.creationMode
          ? mapBrowserToApi[searchFiltersInUri.creationMode]
          : DEFAULT_SEARCH_FILTERS.creationMode,
        page: searchFiltersInUri.page || DEFAULT_PAGE,
        periodBeginningDate:
          searchFiltersInUri.periodBeginningDate || DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate:
          searchFiltersInUri.periodEndingDate || DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    )
  }, [dispatch, query])
  const [isLoading, setIsLoading] = useState(true)
  const [offersCount, setOffersCount] = useState(0)
  const [pageNumber, setPageNumber] = useState(DEFAULT_PAGE)
  const [pageCount, setPageCount] = useState(null)
  const [searchFilters, setSearchFilters] = useState({ ...DEFAULT_SEARCH_FILTERS })
  const [offerer, setOfferer] = useState(null)
  const [isStatusFiltersVisible, setIsStatusFiltersVisible] = useState(false)
  const [areAllOffersSelected, setAreAllOffersSelected] = useState(false)

  const [selectedOfferIds, setSelectedOfferIds] = useState([])
  const savedSearchFilters = useSelector(state => state.offers.searchFilters)
  const offers = useSelector(state => selectOffers(state))

  useEffect(() => {
    setSearchFilters({ ...savedSearchFilters })
    setPageNumber(savedSearchFilters.page)
  }, [savedSearchFilters])

  useEffect(() => {
    if (
      savedSearchFilters.offererId &&
      savedSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
    ) {
      getOfferer(savedSearchFilters.offererId).then(offerer => setOfferer(offerer))
    }
  }, [getOfferer, savedSearchFilters.offererId])

  useEffect(() => {
    if (currentUser.isAdmin) {
      const isVenueFilterSelected = searchFilters.venueId !== DEFAULT_SEARCH_FILTERS.venueId
      const isOffererFilterApplied =
        savedSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
      const isFilterByVenueOrOfferer = isVenueFilterSelected || isOffererFilterApplied

      if (!isFilterByVenueOrOfferer) {
        setSearchFilters(currentSearchFilters => ({
          ...currentSearchFilters,
          status: DEFAULT_SEARCH_FILTERS.status,
        }))
      }
    }
  }, [currentUser.isAdmin, savedSearchFilters.offererId, searchFilters.venueId])

  useEffect(
    function updateUrlMatchingState() {
      let queryParams = Object.keys(savedSearchFilters).reduce((params, field) => {
        const translatedFilterName = mapApiToBrowser[field]
        const isFilterSet = savedSearchFilters[field] !== DEFAULT_SEARCH_FILTERS[field]
        return {
          ...params,
          [translatedFilterName]: isFilterSet ? savedSearchFilters[field] : null,
        }
      }, {})

      const fieldsWithTranslatedValues = ['statut', 'creation']
      fieldsWithTranslatedValues.forEach(field => {
        if (queryParams[field]) {
          const translatedValue = mapApiToBrowser[queryParams[field]]
          queryParams[field] = translatedValue
        }
      })

      query.change(queryParams)
    },
    [query, savedSearchFilters]
  )

  const loadAndUpdateOffers = useCallback(
    filters => {
      dispatch(loadOffers({ ...filters }))
        .then(({ page, pageCount, offersCount }) => {
          setIsLoading(false)
          setOffersCount(offersCount)
          setPageNumber(page)
          setPageCount(pageCount)
        })
        .catch(() => setIsLoading(false))
    },
    [dispatch]
  )

  useEffect(() => {
    Object.keys(savedSearchFilters).length > 0 && loadAndUpdateOffers(savedSearchFilters)
  }, [loadAndUpdateOffers, savedSearchFilters])

  const applyFilters = useCallback(() => {
    setIsLoading(true)
    setIsStatusFiltersVisible(false)
    dispatch(
      saveSearchFilters({
        ...searchFilters,
        page: DEFAULT_PAGE,
      })
    )
  }, [dispatch, searchFilters])

  const removeOfferer = useCallback(() => {
    setIsLoading(true)
    setOfferer(null)
    const updatedFilters = {
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
      page: DEFAULT_PAGE,
    }
    if (
      searchFilters.venueId === DEFAULT_SEARCH_FILTERS.venueId &&
      searchFilters.status !== DEFAULT_SEARCH_FILTERS.status
    ) {
      updatedFilters.status = DEFAULT_SEARCH_FILTERS.status
    }
    dispatch(saveSearchFilters({ ...updatedFilters }))
  }, [dispatch, searchFilters.status, searchFilters.venueId])

  const refreshOffers = useCallback(() => loadAndUpdateOffers(savedSearchFilters), [
    loadAndUpdateOffers,
    savedSearchFilters,
  ])

  const hasSearchFilters = useCallback(
    (searchFilters, filterNames = Object.keys(searchFilters)) => {
      return filterNames
        .map(
          filterName =>
            searchFilters[filterName] !==
            { ...DEFAULT_SEARCH_FILTERS, page: DEFAULT_PAGE }[filterName]
        )
        .includes(true)
    },
    []
  )

  const isAdminForbidden = useCallback(
    searchFilters => {
      return currentUser.isAdmin && !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
    },
    [currentUser.isAdmin, hasSearchFilters]
  )

  const updateStatusFilter = useCallback(selectedStatus => {
    setSearchFilters(currentSearchFilters => ({ ...currentSearchFilters, status: selectedStatus }))
  }, [])

  const onPreviousPageClick = useCallback(() => {
    setIsLoading(true)
    dispatch(saveSearchFilters({ page: pageNumber - 1 }))
    setPageNumber(currentPage => currentPage - 1)
  }, [dispatch, pageNumber])

  const onNextPageClick = useCallback(() => {
    setIsLoading(true)
    dispatch(saveSearchFilters({ page: pageNumber + 1 }))
  }, [dispatch, pageNumber])

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

  const selectAllOffers = useCallback(() => {
    setSelectedOfferIds(
      areAllOffersSelected
        ? []
        : offers.filter(offer => !isOfferDisabled(offer.status)).map(offer => offer.id)
    )

    toggleSelectAllCheckboxes()
  }, [areAllOffersSelected, offers, toggleSelectAllCheckboxes])

  const clearSelectedOfferIds = useCallback(() => {
    setSelectedOfferIds([])
  }, [])

  const resetFilters = useCallback(() => {
    setOfferer(null)
    dispatch(
      saveSearchFilters({
        ...DEFAULT_SEARCH_FILTERS,
      })
    )
  }, [dispatch])

  const { isAdmin } = currentUser || {}
  const hasOffers = offers.length > 0
  const userHasNoOffers = !isLoading && !hasOffers && !hasSearchFilters(savedSearchFilters)

  const actionLink =
    userHasNoOffers || isAdmin ? null : (
      <Link
        className="primary-button with-icon"
        to="/offres/creation"
      >
        <AddOfferSvg />
        {'Créer une offre'}
      </Link>
    )

  const nbSelectedOffers = areAllOffersSelected ? offersCount : selectedOfferIds.length

  return (
    <div className="offers-page">
      <PageTitle title="Vos offres" />
      <Titles
        action={actionLink}
        title="Offres"
      />
      <ActionsBarPortal isVisible={nbSelectedOffers > 0}>
        <ActionsBarContainer
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOfferIds}
          nbSelectedOffers={areAllOffersSelected ? offersCount : selectedOfferIds.length}
          refreshOffers={refreshOffers}
          selectedOfferIds={selectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
        />
      </ActionsBarPortal>
      {userHasNoOffers ? (
        <NoOffers />
      ) : (
        <>
          <h3 className="op-title">
            {'Rechercher une offre'}
          </h3>
          {hasSearchFilters(savedSearchFilters) ? (
            <Link
              className="reset-filters-link"
              onClick={resetFilters}
              to="/offres"
            >
              {'Réinitialiser les filtres'}
            </Link>
          ) : (
            <span className="reset-filters-link disabled">
              {'Réinitialiser les filtres'}
            </span>
          )}

          <SearchFilters
            applyFilters={applyFilters}
            offerer={offerer}
            removeOfferer={removeOfferer}
            selectedFilters={searchFilters}
            setSearchFilters={setSearchFilters}
          />

          <div
            aria-busy={isLoading}
            aria-live="polite"
            className="section"
          >
            {isLoading ? (
              <Spinner />
            ) : (
              <>
                {hasOffers && (
                  <div className="offers-count">
                    {`${offersCount} ${offersCount <= 1 ? 'offre' : 'offres'}`}
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
                    offers={offers}
                    selectOffer={selectOffer}
                    selectedOfferIds={selectedOfferIds}
                  />
                </table>
                {hasOffers && (
                  <div className="pagination">
                    <button
                      disabled={pageNumber === 1}
                      onClick={onPreviousPageClick}
                      type="button"
                    >
                      <Icon
                        alt="Aller à la page précédente"
                        svg="ico-left-arrow"
                      />
                    </button>
                    <span>
                      {`Page ${pageNumber}/${pageCount}`}
                    </span>
                    <button
                      disabled={pageNumber === pageCount}
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
                {!hasOffers && hasSearchFilters(savedSearchFilters) && (
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
  query: PropTypes.shape({
    change: PropTypes.func.isRequired,
    parse: PropTypes.func.isRequired,
  }).isRequired,
}

export default Offers
