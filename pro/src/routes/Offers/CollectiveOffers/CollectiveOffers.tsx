import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router-dom'

import { api } from 'api/v1/api'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { filterEducationalCategories } from 'core/OfferEducational'
import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import {
  Audience,
  Offer,
  Offerer,
  Option,
  TSearchFilters,
} from 'core/Offers/types'
import OffersScreen from 'screens/Offers'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { getFilteredCollectiveOffersAdapter } from '../adapters'

interface ICollectiveOffersProps {
  urlPageNumber: number
  urlSearchFilters: TSearchFilters
  offerer: Offerer | null
  setOfferer: (offerer: Offerer | null) => void
  separateIndividualAndCollectiveOffers: boolean
  venues: Option[]
}

const CollectiveOffers = ({
  urlPageNumber,
  urlSearchFilters,
  offerer,
  setOfferer,
  separateIndividualAndCollectiveOffers,
  venues,
}: ICollectiveOffersProps): JSX.Element => {
  const history = useHistory()
  const notify = useNotification()
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<TSearchFilters | null>(null)
  const [categories, setCategories] = useState<Option[]>([])

  const loadAndUpdatCollectiveOffers = useCallback(
    async (filters: TSearchFilters) => {
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
      const newUrl = computeOffersUrl(filters, filters.page)

      history.push(newUrl)
    },
    [history]
  )

  useEffect(() => {
    const filters = { ...DEFAULT_SEARCH_FILTERS, ...urlSearchFilters }
    if (currentUser.isAdmin) {
      const isVenueFilterSelected =
        urlSearchFilters.venueId !== DEFAULT_SEARCH_FILTERS.venueId
      const isOffererFilterApplied =
        urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
      const isFilterByVenueOrOfferer =
        isVenueFilterSelected || isOffererFilterApplied

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
  }, [offerer?.id])

  if (!initialSearchFilters) {
    return <Spinner />
  }

  return (
    <OffersScreen
      categories={categories}
      currentPageNumber={urlPageNumber ?? DEFAULT_PAGE}
      currentUser={currentUser}
      initialSearchFilters={initialSearchFilters}
      isLoading={isLoading}
      loadAndUpdateOffers={loadAndUpdatCollectiveOffers}
      offerer={offerer}
      offers={offers}
      redirectWithUrlFilters={redirectWithUrlFilters}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setIsLoading={setIsLoading}
      setOfferer={setOfferer}
      urlAudience={Audience.COLLECTIVE}
      urlSearchFilters={urlSearchFilters}
      venues={venues}
    />
  )
}

export default CollectiveOffers
