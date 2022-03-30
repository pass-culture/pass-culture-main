import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router-dom'

import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience, Offer, Offerer, TSearchFilters } from 'core/Offers/types'
import { hasSearchFilters } from 'core/Offers/utils'
import OffersScreen from 'screens/Offers'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { getFilteredCollectiveOffersAdapter } from '../adapters'

interface ICollectiveOffersProps {
  urlPageNumber: number
  urlSearchFilters: TSearchFilters
  offerer: Offerer | null
  setOfferer: (offerer: Offerer | null) => void
  separateIndividualAndCollectiveOffers: boolean
}

const CollectiveOffers = ({
  urlPageNumber,
  urlSearchFilters,
  offerer,
  setOfferer,
  separateIndividualAndCollectiveOffers,
}: ICollectiveOffersProps): JSX.Element => {
  const history = useHistory()
  const notify = useNotification()
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()

  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<TSearchFilters | null>(null)

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
    if (initialSearchFilters) {
      dispatch(
        saveSearchFilters({
          ...initialSearchFilters,
          status: urlSearchFilters.status,
        })
      )
    }
  }, [dispatch, urlSearchFilters, initialSearchFilters])

  useEffect(() => {
    dispatch(savePageNumber(urlPageNumber))
  }, [dispatch, urlPageNumber])

  if (!initialSearchFilters) {
    return <Spinner />
  }

  return (
    <OffersScreen
      currentPageNumber={urlPageNumber}
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
    />
  )
}

export default CollectiveOffers
