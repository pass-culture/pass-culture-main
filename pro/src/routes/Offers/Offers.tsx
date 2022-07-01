import { DEFAULT_SEARCH_FILTERS, hasSearchFilters } from 'core/Offers'
import { Offer, Offerer, Option, TSearchFilters } from 'core/Offers/types'
import React, { useCallback, useEffect, useState } from 'react'
import {
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from 'repository/venuesService'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { Audience } from 'core/shared'
import OffersScreen from 'screens/Offers'
import Spinner from 'components/layout/Spinner'
import { api } from 'apiClient/api'
import { computeOffersUrl } from 'core/Offers/utils'
import { getFilteredOffersAdapter } from './adapters'
import { getOffererAdapter } from 'core/Offers/adapters'
import { sortByDisplayName } from 'utils/strings'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router-dom'
import useNotification from 'components/hooks/useNotification'
import { useQuerySearchFilters } from 'core/Offers/hooks'

const Offers = (): JSX.Element => {
  const [urlSearchFilters, urlPageNumber] = useQuerySearchFilters()
  const notify = useNotification()
  const history = useHistory()
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<TSearchFilters | null>(null)
  const [venues, setVenues] = useState<Option[]>([])
  const [categories, setCategories] = useState<Option[]>([])

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

  const loadAndUpdateOffers = useCallback(
    async (filters: TSearchFilters) => {
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
    const loadCategories = () =>
      api.getCategories().then(categoriesAndSubcategories => {
        const categoriesOptions = categoriesAndSubcategories.categories
          .filter(category => category.isSelectable)
          .map(category => ({
            id: category.id,
            displayName: category.proLabel,
          }))

        setCategories(sortByDisplayName(categoriesOptions))
      })

    loadCategories()
  }, [])

  const redirectWithUrlFilters = useCallback(
    (
      filters: TSearchFilters & {
        page?: number
        audience?: Audience
      }
    ) => {
      const newUrl = computeOffersUrl(filters, filters.page)

      history.push(newUrl)
    },
    [history]
  )

  useEffect(() => {
    const filters = { ...urlSearchFilters }
    if (currentUser.isAdmin) {
      const isFilterByVenueOrOfferer = hasSearchFilters(urlSearchFilters, [
        'venueId',
        'offererId',
      ])

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

  useEffect(() => {
    const loadAllVenuesByProUser = () =>
      fetchAllVenuesByProUser(offerer?.id).then(venues =>
        setVenues(formatAndOrderVenues(venues))
      )

    loadAllVenuesByProUser()
  }, [offerer?.id])

  if (!initialSearchFilters) {
    return <Spinner />
  }

  return (
    <OffersScreen
      audience={Audience.INDIVIDUAL}
      categories={categories}
      currentPageNumber={urlPageNumber}
      currentUser={currentUser}
      initialSearchFilters={initialSearchFilters}
      isLoading={isLoading}
      loadAndUpdateOffers={loadAndUpdateOffers}
      offerer={offerer}
      offers={offers}
      redirectWithUrlFilters={redirectWithUrlFilters}
      setOfferer={setOfferer}
      urlSearchFilters={urlSearchFilters}
      venues={venues}
    />
  )
}

export default Offers
