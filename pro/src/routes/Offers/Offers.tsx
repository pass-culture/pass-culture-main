import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Offer, Offerer, SearchFilters } from 'core/Offers/types'
import OffersScreen from 'screens/Offers'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { getFilteredOffersAdapter, getOffererAdapter } from './adapters'

const Offers = (): JSX.Element => {
  const notify = useNotification()
  const [urlSearchFilters, urlPageNumber] = useQuerySearchFilters()
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [isRefreshingOffers, setIsRefreshingOffers] = useState(true)
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  })
  const [offers, setOffers] = useState<Offer[]>([])
  const [offersCount, setOffersCount] = useState(0)
  const [pageCount, setPageCount] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentPageNumber, setCurrentPageNumber] = useState(DEFAULT_PAGE)

  const loadAndUpdateOffers = useCallback(
    async (filters: SearchFilters) => {
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...filters,
      }
      const { isOk, message, payload } = await getFilteredOffersAdapter(
        apiFilters
      )

      if (!isOk) {
        setIsLoading(false)
        return notify.error(message)
      }

      const offersCount = payload.offers.length
      setIsLoading(false)
      setOffersCount(offersCount)
      const pageCount = Math.ceil(offersCount / NUMBER_OF_OFFERS_PER_PAGE)
      const cappedPageCount = Math.min(pageCount, MAX_TOTAL_PAGES)
      setPageCount(cappedPageCount)
      setOffers(payload.offers)
    },
    [notify]
  )

  useEffect(() => {
    const loadOfferer = async () => {
      if (
        urlSearchFilters.offererId &&
        urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
      ) {
        const { isOk, message, payload } = await getOffererAdapter(
          urlSearchFilters.offererId
        )

        if (!isOk) {
          return notify.error(message)
        }

        setOfferer(payload)
      }
    }

    loadOfferer()
  }, [urlSearchFilters.offererId, notify])

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
  }, [
    currentUser.isAdmin,
    urlSearchFilters.offererId,
    searchFilters.venueId,
    setSearchFilters,
  ])

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

  return (
    <OffersScreen
      currentPageNumber={currentPageNumber}
      currentUser={currentUser}
      isLoading={isLoading}
      loadAndUpdateOffers={loadAndUpdateOffers}
      offerer={offerer}
      offers={offers}
      offersCount={offersCount}
      pageCount={pageCount}
      searchFilters={searchFilters}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setIsLoading={setIsLoading}
      setIsRefreshingOffers={setIsRefreshingOffers}
      setOfferer={setOfferer}
      setSearchFilters={setSearchFilters}
      urlSearchFilters={urlSearchFilters}
    />
  )
}

export default Offers
