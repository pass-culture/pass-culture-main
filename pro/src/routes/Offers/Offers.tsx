import React, { useEffect, useState } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Audience, Offerer, Option } from 'core/Offers/types'
import {
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from 'repository/venuesService'

import { getOffererAdapter } from './adapters'
import CollectiveOffers from './CollectiveOffers'
import IndividualOffers from './IndividualOffers'

const Offers = (): JSX.Element => {
  const [urlSearchFilters, urlPageNumber, urlAudience] = useQuerySearchFilters()
  const notify = useNotification()

  const [offerer, setOfferer] = useState<Offerer | null>(null)
  const [venues, setVenues] = useState<Option[]>([])

  const separateIndividualAndCollectiveOffers = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
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
    const loadAllVenuesByProUser = () =>
      fetchAllVenuesByProUser(offerer?.id).then(venues =>
        setVenues(formatAndOrderVenues(venues))
      )

    loadAllVenuesByProUser()
  }, [offerer?.id])

  return urlAudience === Audience.INDIVIDUAL ? (
    <IndividualOffers
      offerer={offerer}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlPageNumber={urlPageNumber}
      urlSearchFilters={urlSearchFilters}
      venues={venues}
    />
  ) : (
    <CollectiveOffers
      offerer={offerer}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlPageNumber={urlPageNumber}
      urlSearchFilters={urlSearchFilters}
      venues={venues}
    />
  )
}

export default Offers
