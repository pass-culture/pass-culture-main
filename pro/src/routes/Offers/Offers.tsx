import React, { useEffect, useState } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import { Audience, Offerer } from 'core/Offers/types'

import { getOffererAdapter } from './adapters'
import CollectiveOffers from './CollectiveOffers'
import IndividualOffers from './IndividualOffers'

const Offers = (): JSX.Element => {
  const [urlSearchFilters, urlPageNumber, urlAudience] = useQuerySearchFilters()
  const notify = useNotification()

  const [offerer, setOfferer] = useState<Offerer | null>(null)

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

  return urlAudience === Audience.INDIVIDUAL ? (
    <IndividualOffers
      offerer={offerer}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlPageNumber={urlPageNumber}
      urlSearchFilters={urlSearchFilters}
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
    />
  )
}

export default Offers
