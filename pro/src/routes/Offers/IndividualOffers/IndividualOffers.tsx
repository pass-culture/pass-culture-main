import React, { useCallback, useEffect, useState } from 'react'

import { api } from 'api/v1/api'
import { SharedCurrentUserResponseModel } from 'api/v1/gen'
import useNotification from 'components/hooks/useNotification'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import {
  Audience,
  Offer,
  Offerer,
  Option,
  TSearchFilters,
} from 'core/Offers/types'
import OffersScreen from 'screens/Offers'

import { getFilteredOffersAdapter } from '../adapters'

interface IIndividualOffersProps {
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
  venues: Option[]
}

const IndividualOffers = ({
  urlPageNumber,
  initialSearchFilters,
  offerer,
  setOfferer,
  separateIndividualAndCollectiveOffers,
  currentUser,
  redirectWithUrlFilters,
  venues,
}: IIndividualOffersProps): JSX.Element => {
  const notify = useNotification()

  const [offers, setOffers] = useState<Offer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [categories, setCategories] = useState<Option[]>([])

  const loadAndUpdateOffers = useCallback(
    async (filters: TSearchFilters) => {
      setIsLoading(true)
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
      api.getOffersGetCategories().then(categoriesAndSubcategories => {
        const categoriesOptions = categoriesAndSubcategories.categories
          .filter(category => category.isSelectable)
          .map(category => ({
            id: category.id,
            displayName: category.proLabel,
          }))

        setCategories(
          categoriesOptions.sort((a, b) =>
            a.displayName.localeCompare(b.displayName)
          )
        )
      })

    loadCategories()
  }, [])

  return (
    <OffersScreen
      categories={categories}
      currentPageNumber={urlPageNumber}
      currentUser={currentUser}
      initialSearchFilters={initialSearchFilters}
      isLoading={isLoading}
      loadAndUpdateOffers={loadAndUpdateOffers}
      offerer={offerer}
      offers={offers}
      redirectWithUrlFilters={redirectWithUrlFilters}
      separateIndividualAndCollectiveOffers={
        separateIndividualAndCollectiveOffers
      }
      setOfferer={setOfferer}
      urlAudience={Audience.INDIVIDUAL}
      venues={venues}
    />
  )
}

export default IndividualOffers
