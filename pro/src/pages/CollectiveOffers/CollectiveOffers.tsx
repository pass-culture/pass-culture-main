import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  GetOffererResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { getOffererAdapter } from 'core/Offers/adapters'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import {
  hasSearchFilters,
  computeCollectiveOffersUrl,
  serializeApiFilters,
} from 'core/Offers/utils'
import { Audience } from 'core/shared/types'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { formatAndOrderVenues } from 'repository/venuesService'
import OffersScreen from 'screens/Offers'
import Spinner from 'ui-kit/Spinner/Spinner'

export const GET_COLLECTIVE_OFFERS_QUERY_KEY = 'getCollectiveOffers'

export const CollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const notify = useNotification()
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const [offerer, setOfferer] = useState<GetOffererResponseModel | null>(null)
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

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const offersQuery = useSWR(
    [GET_COLLECTIVE_OFFERS_QUERY_KEY, apiFilters],
    () => {
      const {
        nameOrIsbn,
        offererId,
        venueId,
        categoryId,
        status,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        collectiveOfferType,
        format,
      } = serializeApiFilters(apiFilters)

      return api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status as CollectiveOfferDisplayedStatus,
        venueId,
        categoryId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        collectiveOfferType,
        format
      )
    },
    { fallbackData: [] }
  )

  return (
    <AppLayout>
      {!initialSearchFilters || offersQuery.isLoading ? (
        <Spinner />
      ) : (
        <OffersScreen
          audience={Audience.COLLECTIVE}
          currentPageNumber={currentPageNumber}
          currentUser={currentUser}
          initialSearchFilters={initialSearchFilters}
          isLoading={offersQuery.isLoading}
          offerer={offerer}
          offers={offersQuery.data}
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
