import { useEffect, useState } from 'react'
import { RouteObject, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { getOffererAdapter } from 'core/Offers/adapters'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { Offerer, SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters, computeIndividualOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { formatAndOrderVenues } from 'repository/venuesService'
import OffersScreen from 'screens/Offers'
import { parse } from 'utils/query-string'
import { sortByLabel } from 'utils/strings'
import { translateQueryParamsToApiParams } from 'utils/translate'

import { getFilteredOffersAdapter } from './adapters/getFilteredOffersAdapter'

export const OffersRoute = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const notify = useNotification()
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<SearchFiltersParams | null>(null)
  const [venues, setVenues] = useState<SelectOption[]>([])
  const [categories, setCategories] = useState<SelectOption[]>([])

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
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadOfferer()
  }, [urlSearchFilters.offererId, notify])

  useEffect(() => {
    const loadCategories = () =>
      api.getCategories().then((categoriesAndSubcategories) => {
        const categoriesOptions = categoriesAndSubcategories.categories
          .filter((category) => category.isSelectable)
          .map((category) => ({
            value: category.id,
            label: category.proLabel,
          }))

        setCategories(sortByLabel(categoriesOptions))
      })

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadCategories()
  }, [])

  const redirectWithUrlFilters = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    navigate(computeIndividualOffersUrl(filters))
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
    const loadAllVenuesByProUser = async () => {
      const venuesResponse = await getVenuesForOffererAdapter({
        offererId: offerer?.id.toString(),
      })
      if (venuesResponse.isOk) {
        setVenues(formatAndOrderVenues(venuesResponse.payload))
      } else {
        return notify.error(venuesResponse.message)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadAllVenuesByProUser()
  }, [offerer?.id, notify])

  return (
    <AppLayout>
      <OffersScreen
        audience={Audience.INDIVIDUAL}
        categories={categories}
        currentPageNumber={currentPageNumber}
        currentUser={currentUser}
        initialSearchFilters={initialSearchFilters ?? DEFAULT_SEARCH_FILTERS}
        offerer={offerer}
        redirectWithUrlFilters={redirectWithUrlFilters}
        setOfferer={setOfferer}
        urlSearchFilters={urlSearchFilters}
        venues={venues}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OffersRoute

// ts-unused-exports:disable-next-line
export const loader: RouteObject['loader'] = async ({
  request,
}): Promise<{
  offers: ListOffersOfferResponseModel[]
}> => {
  console.log('loader')
  const { url } = request
  const urlSearchFilters = translateQueryParamsToApiParams(
    parse(url.split('?')[1])
  )

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  }

  const { payload } = await getFilteredOffersAdapter(apiFilters)
  return payload
}

// Used to manually retrigger loader (call it with fetcher.submit)
// ts-unused-exports:disable-next-line
export const action: RouteObject['action'] = () => null

// since it's not real pagination (front pagination only here)
// we don't need to revalidate on page change
// ts-unused-exports:disable-next-line
export const shouldRevalidate: RouteObject['shouldRevalidate'] = ({
  currentUrl,
  nextUrl,
  formAction,
}) => {
  // Allow revalidation by using actions
  if (formAction) {
    return true
  }

  const keysToIgnore = ['page']
  const currentSearchParams = new URLSearchParams(currentUrl.search)
  const nextSearchParams = new URLSearchParams(nextUrl.search)
  const currentSearchEntries = Array.from(currentSearchParams.entries()).filter(
    ([key]) => !keysToIgnore.includes(key)
  )
  const nextSearchEntries = Array.from(nextSearchParams.entries()).filter(
    ([key]) => !keysToIgnore.includes(key)
  )
  // Only reload offers when search filters change, not when page changes
  const shouldRevalidate =
    JSON.stringify(currentSearchEntries) !== JSON.stringify(nextSearchEntries)

  return shouldRevalidate
}
