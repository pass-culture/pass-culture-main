import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

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

import { getFilteredCollectiveOffersAdapter } from './adapters'

export const CollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const notify = useNotification()
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [offers, setOffers] = useState<CollectiveOfferResponseModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
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

  const loadAndUpdateOffers = useCallback(
    async (filters: SearchFiltersParams) => {
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
          isLoading={isLoading}
          loadAndUpdateOffers={loadAndUpdateOffers}
          offerer={offerer}
          offers={offers}
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
