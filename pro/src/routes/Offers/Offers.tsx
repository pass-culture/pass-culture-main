import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { DEFAULT_SEARCH_FILTERS, hasSearchFilters } from 'core/Offers'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Audience, Offerer, TSearchFilters } from 'core/Offers/types'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'

import { getOffererAdapter } from './adapters'
import CollectiveOffers from './CollectiveOffers'
import IndividualOffers from './IndividualOffers'

const Offers = (): JSX.Element => {
  const history = useHistory()
  const dispatch = useDispatch()
  const { currentUser } = useCurrentUser()
  const [urlSearchFilters, urlPageNumber, urlAudience] = useQuerySearchFilters()
  const [initialSearchFilters, setInitialSearchFilters] =
    useState<TSearchFilters | null>(null)
  const notify = useNotification()

  const [offerer, setOfferer] = useState<Offerer | null>(null)

  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  const redirectWithUrlFilters = useCallback(
    (
      filters: TSearchFilters & {
        page?: number
        audience?: Audience
      }
    ) => {
      setInitialSearchFilters(null)
      const { page, audience, ...searchFilters } = filters
      const newUrl = computeOffersUrl(searchFilters, page, audience)

      history.push(newUrl)
    },
    [history]
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

  return urlAudience === Audience.INDIVIDUAL ? (
    <IndividualOffers
      currentUser={currentUser}
      initialSearchFilters={initialSearchFilters}
      offerer={offerer}
      redirectWithUrlFilters={redirectWithUrlFilters}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlPageNumber={urlPageNumber}
    />
  ) : (
    <CollectiveOffers
      currentUser={currentUser}
      initialSearchFilters={initialSearchFilters}
      offerer={offerer}
      redirectWithUrlFilters={redirectWithUrlFilters}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlPageNumber={urlPageNumber}
    />
  )
}

export default Offers
