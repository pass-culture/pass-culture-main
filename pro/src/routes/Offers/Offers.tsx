import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
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
  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<SearchFilters | null>(null)

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

      setIsLoading(false)
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
    const filters = { ...DEFAULT_SEARCH_FILTERS, ...urlSearchFilters }
    if (currentUser.isAdmin) {
      const isVenueFilterSelected =
        urlSearchFilters.venueId !== DEFAULT_SEARCH_FILTERS.venueId
      const isOffererFilterApplied =
        urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
      const isFilterByVenueOrOfferer =
        isVenueFilterSelected || isOffererFilterApplied

      if (!isFilterByVenueOrOfferer) {
        filters.status = DEFAULT_SEARCH_FILTERS.status
      }
    }
    setInitialSearchFilters(filters)
  }, [setInitialSearchFilters, urlSearchFilters, currentUser.isAdmin])

  useEffect(() => {
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

  if (!initialSearchFilters) {
    return <Spinner />
  }

  return (
    <OffersScreen
      currentPageNumber={urlPageNumber ?? DEFAULT_PAGE}
      currentUser={currentUser}
      initialSearchFilters={initialSearchFilters}
      isLoading={isLoading}
      loadAndUpdateOffers={loadAndUpdateOffers}
      offerer={offerer}
      offers={offers}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setIsLoading={setIsLoading}
      setOfferer={setOfferer}
      urlSearchFilters={urlSearchFilters}
    />
  )
}

export default Offers
