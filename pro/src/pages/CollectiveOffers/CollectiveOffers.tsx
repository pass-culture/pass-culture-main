import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { filterEducationalCategories } from 'core/OfferEducational'
import { getOffererAdapter } from 'core/Offers/adapters'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Offer, Offerer, Option, TSearchFilters } from 'core/Offers/types'
import { hasSearchFilters, computeCollectiveOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared/types'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { formatAndOrderVenues } from 'repository/venuesService'
import OffersScreen from 'screens/Offers'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByDisplayName } from 'utils/strings'

import { getFilteredCollectiveOffersAdapter } from './adapters'

const CollectiveOffers = (): JSX.Element => {
  const [urlSearchFilters, urlPageNumber] = useQuerySearchFilters()
  const notify = useNotification()
  const navigate = useNavigate()
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
      getVenuesForOffererAdapter({
        offererId: offerer?.nonHumanizedId.toString(),
      }).then(venuesResponse =>
        setVenues(formatAndOrderVenues(venuesResponse.payload))
      )

    loadAllVenuesByProUser()
  }, [offerer?.nonHumanizedId])

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

  const redirectWithUrlFilters = (
    filters: TSearchFilters & {
      page?: number
      audience?: Audience
    }
  ) => {
    const newUrl = computeCollectiveOffersUrl(filters, filters.page)
    navigate(newUrl)
  }

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
