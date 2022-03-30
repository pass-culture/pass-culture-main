import React, { useCallback, useState } from 'react'

import { SharedCurrentUserResponseModel } from 'api/v1/gen'
import useNotification from 'components/hooks/useNotification'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience, Offer, Offerer, TSearchFilters } from 'core/Offers/types'
import OffersScreen from 'screens/Offers'

import { getFilteredCollectiveOffersAdapter } from '../adapters'

interface ICollectiveOffersProps {
  urlPageNumber: number
  initialSearchFilters: TSearchFilters
  offerer: Offerer | null
  setOfferer: (offerer: Offerer | null) => void
  separateIndividualAndCollectiveOffers: boolean
  currentUser: SharedCurrentUserResponseModel
  redirectWithUrlFilters: (
    filters: TSearchFilters & {
      page?: number
      audience?: Audience
    }
  ) => void
}

const CollectiveOffers = ({
  urlPageNumber,
  initialSearchFilters,
  offerer,
  setOfferer,
  separateIndividualAndCollectiveOffers,
  currentUser,
  redirectWithUrlFilters,
}: ICollectiveOffersProps): JSX.Element => {
  const notify = useNotification()

  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const loadAndUpdatCollectiveOffers = useCallback(
    async (filters: TSearchFilters) => {
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
      setOfferer={setOfferer}
      urlAudience={Audience.COLLECTIVE}
    />
  )
}

export default CollectiveOffers
