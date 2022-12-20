import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useHistory, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { useAppContext } from 'app/AppContext'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Offer, Option, TSearchFilters } from 'core/Offers/types'
import { computeOffersUrl } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import OffersScreen from 'screens/Offers'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByDisplayName } from 'utils/strings'

import { getFilteredOffersAdapter } from './adapters'

const OffersRoute = (): JSX.Element => {
  const [urlSearchFilters, urlPageNumber] = useQuerySearchFilters()
  const notify = useNotification()
  const history = useHistory()
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const { venueId } = useParams<{ venueId: string }>()
  const { selectedVenue } = useAppContext()

  const [initialSearchFilters, setInitialSearchFilters] =
    useState<TSearchFilters | null>(null)
  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [categories, setCategories] = useState<Option[]>([])

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
    dispatch(
      saveSearchFilters({
        nameOrIsbn:
          urlSearchFilters.nameOrIsbn || DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        venueId,
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
    const filters = { ...urlSearchFilters }
    if (venueId !== undefined) {
      filters.venueId = venueId
    }
    setInitialSearchFilters(filters)
  }, [setInitialSearchFilters, urlSearchFilters, venueId])

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
      offers={offers}
      redirectWithUrlFilters={redirectWithUrlFilters}
      urlSearchFilters={urlSearchFilters}
      venueName={
        venueId && selectedVenue !== null ? selectedVenue.name : undefined
      }
    />
  )
}

export default OffersRoute
