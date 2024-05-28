import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import { computeOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { Audience } from 'core/shared/types'
import useCurrentUser from 'hooks/useCurrentUser'
import { formatAndOrderVenues } from 'repository/venuesService'
import { Offers } from 'screens/Offers/Offers'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

export const GET_OFFERS_QUERY_KEY = 'listOffers'

export const OffersRoute = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const [initialSearchFilters, setInitialSearchFilters] =
    useState<SearchFiltersParams | null>(null)

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, urlSearchFilters.offererId],
    ([, offererIdParam]) =>
      urlSearchFilters.offererId === DEFAULT_SEARCH_FILTERS.offererId
        ? null
        : api.getOfferer(Number(offererIdParam)),
    { fallbackData: null }
  )
  const offerer = offererQuery.data

  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  const categoriesOptions = sortByLabel(
    categoriesQuery.data.categories
      .filter((category) => category.isSelectable)
      .map((category) => ({
        value: category.id,
        label: category.proLabel,
      }))
  )

  const redirectWithUrlFilters = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    navigate(computeOffersUrl(filters))
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

  const { data } = useSWR(
    [GET_VENUES_QUERY_KEY, offerer?.id],
    ([, offererIdParam]) => api.getVenues(null, null, offererIdParam),
    { fallbackData: { venues: [] } }
  )
  const venues = formatAndOrderVenues(data.venues)

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const offersQuery = useSWR([GET_OFFERS_QUERY_KEY, apiFilters], () => {
    const {
      nameOrIsbn,
      offererId,
      venueId,
      categoryId,
      status,
      creationMode,
      periodBeginningDate,
      periodEndingDate,
    } = serializeApiFilters(apiFilters)

    return api.listOffers(
      nameOrIsbn,
      offererId,
      status,
      venueId,
      categoryId,
      creationMode,
      periodBeginningDate,
      periodEndingDate
    )
  })

  const offers = offersQuery.data || []

  return (
    <AppLayout>
      {!initialSearchFilters ||
      offersQuery.isLoading ||
      offererQuery.isLoading ? (
        <Spinner />
      ) : (
        <Offers
          audience={Audience.INDIVIDUAL}
          categories={categoriesOptions}
          currentPageNumber={currentPageNumber}
          currentUser={currentUser}
          initialSearchFilters={initialSearchFilters}
          isLoading={offersQuery.isLoading}
          offerer={offerer}
          offers={offers}
          redirectWithUrlFilters={redirectWithUrlFilters}
          urlSearchFilters={urlSearchFilters}
          venues={venues}
        />
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OffersRoute
