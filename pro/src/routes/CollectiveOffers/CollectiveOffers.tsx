import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { Redirect, useHistory } from 'react-router-dom'

import { api } from 'api/api'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { filterEducationalCategories } from 'core/OfferEducational'
import { getOffererAdapter } from 'core/Offers/adapters'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Offer, Offerer, TSearchFilters, Option } from 'core/Offers/types'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import { hasSearchFilters } from 'core/Offers/utils'
import { Audience } from 'core/shared/types'
import {
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from 'repository/venuesService'
import OffersScreen from 'screens/Offers'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { getFilteredCollectiveOffersAdapter } from './adapters'

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

  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
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
    const loadCategories = () => {
      api.getOffersGetCategories().then(categoriesAndSubcategories => {
        const categoriesOptions = filterEducationalCategories(
          categoriesAndSubcategories
        ).educationalCategories.map(category => ({
          id: category.id,
          displayName: category.label,
        }))

        setCategories(
          categoriesOptions.sort((a, b) =>
            a.displayName.localeCompare(b.displayName)
          )
        )
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

  if (!separateIndividualAndCollectiveOffers) {
    return <Redirect to="/offres" />
  }

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
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlSearchFilters={urlSearchFilters}
      venues={venues}
    />
  )
}

export default CollectiveOffers
