import { useEffect, useState } from 'react'
import { RouteObject, useNavigate } from 'react-router-dom'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { getOffererAdapter } from 'core/Offers/adapters'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { Offerer, SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters, computeCollectiveOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared/types'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { formatAndOrderVenues } from 'repository/venuesService'
import OffersScreen from 'screens/Offers'
import Spinner from 'ui-kit/Spinner/Spinner'
import { parse } from 'utils/query-string'
import { translateQueryParamsToApiParams } from 'utils/translate'

import { getFilteredCollectiveOffersAdapter } from './adapters'

export const CollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const notify = useNotification()
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<SearchFiltersParams | null>(null)
  const [venues, setVenues] = useState<SelectOption[]>([])

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
    const loadAllVenuesByProUser = async () => {
      const venuesResponse = await getVenuesForOffererAdapter({
        offererId: offerer?.id.toString(),
      })
      setVenues(formatAndOrderVenues(venuesResponse.payload))
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadAllVenuesByProUser()
  }, [offerer?.id])

  const redirectWithUrlFilters = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    navigate(computeCollectiveOffersUrl(filters))
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

  return (
    <AppLayout>
      {!initialSearchFilters ? (
        <Spinner />
      ) : (
        <OffersScreen
          audience={Audience.COLLECTIVE}
          currentPageNumber={currentPageNumber}
          currentUser={currentUser}
          initialSearchFilters={initialSearchFilters}
          offerer={offerer}
          redirectWithUrlFilters={redirectWithUrlFilters}
          setOfferer={setOfferer}
          urlSearchFilters={urlSearchFilters}
          venues={venues}
        />
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveOffers

// ts-unused-exports:disable-next-line
export const loader: RouteObject['loader'] = async ({
  request,
}): Promise<{
  offers: CollectiveOfferResponseModel[]
}> => {
  const { url } = request
  const urlSearchFilters = translateQueryParamsToApiParams(
    parse(url.split('?')[1])
  )

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  }

  const { payload } = await getFilteredCollectiveOffersAdapter(apiFilters)
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

  // Only reload offers when search filters change, not when page changes
  const shouldRevalidate =
    currentUrl.search === nextUrl.search
      ? false
      : new URLSearchParams(currentUrl.search).get('page') !==
          new URLSearchParams(nextUrl.search).get('page')
        ? false
        : true

  return shouldRevalidate
}
