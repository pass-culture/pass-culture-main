import { Offer, Offerer, Option, TSearchFilters } from 'core/Offers/types'
import React, { useCallback, useEffect, useState } from 'react'
import {
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from 'repository/venuesService'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { Audience } from 'core/shared/types'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import OffersScreen from 'screens/Offers'
import Spinner from 'components/layout/Spinner'
import { api } from 'apiClient/api'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { filterEducationalCategories } from 'core/OfferEducational'
import { getFilteredCollectiveOffersAdapter } from './adapters'
import { getOffererAdapter } from 'core/Offers/adapters'
import { hasSearchFilters } from 'core/Offers/utils'
import { sortByDisplayName } from 'utils/strings'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router-dom'
import useNotification from 'components/hooks/useNotification'
import { useQuerySearchFilters } from 'core/Offers/hooks'

const CollectiveOffers = (): JSX.Element => {
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

  useEffect(() => {
    const loadCategories = () => {
      api.getCategories().then(categoriesAndSubcategories => {
        const categoriesOptions = filterEducationalCategories(
          categoriesAndSubcategories
        ).educationalCategories.map(category => ({
          id: category.id,
          displayName: category.label,
        }))

        setCategories(sortByDisplayName(categoriesOptions))
      })
    }

    loadCategories()
  }, [])

  useEffect(() => {
    const loadAllVenuesByProUser = () =>
      fetchAllVenuesByProUser(offerer?.id).then(venues =>
        setVenues(formatAndOrderVenues(venues))
      )

    loadAllVenuesByProUser()
  }, [offerer?.id])

  const loadAndUpdateOffers = useCallback(
    async (filters: TSearchFilters) => {
      setIsLoading(true)
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...filters,
      }
      const { isOk, message, payload } =
        await getFilteredCollectiveOffersAdapter(apiFilters)

      if (!isOk) {
        setIsLoading(false)
        return notify.error(message)
      }

      setIsLoading(false)
      setOffers(payload.offers)
    },
    [notify]
  )

  const redirectWithUrlFilters = useCallback(
    (
      filters: TSearchFilters & {
        page?: number
        audience?: Audience
      }
    ) => {
      const newUrl = computeCollectiveOffersUrl(filters, filters.page)

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
      audience={Audience.COLLECTIVE}
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

export default CollectiveOffers
