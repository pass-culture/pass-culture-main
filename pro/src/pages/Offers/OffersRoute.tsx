import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { getOffererAdapter } from 'core/Offers/adapters'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { Offerer, SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters, computeOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { formatAndOrderVenues } from 'repository/venuesService'
import OffersScreen from 'screens/Offers'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import { getFilteredOffersAdapter } from './adapters/getFilteredOffersAdapter'

export const OffersRoute = (): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const notify = useNotification()
  const navigate = useNavigate()
  const { currentUser } = useCurrentUser()

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [offers, setOffers] = useState<ListOffersOfferResponseModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
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

  const loadAndUpdateOffers = useCallback(
    async (filters: SearchFiltersParams) => {
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...filters,
      }
      const { isOk, message, payload } =
        await getFilteredOffersAdapter(apiFilters)

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
  }, [offerer?.id])

  return (
    <AppLayout>
      {!initialSearchFilters ? (
        <Spinner />
      ) : (
        <OffersScreen
          audience={Audience.INDIVIDUAL}
          categories={categories}
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
export const Component = OffersRoute
