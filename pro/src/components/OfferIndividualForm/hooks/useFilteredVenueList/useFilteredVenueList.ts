import { useEffect, useState } from 'react'

import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

export interface IUseFilteredVenueListProps {
  subCategories: IOfferSubCategory[]
  subcategoryId: string
  venueList: TOfferIndividualVenue[]
}

const useFilteredVenueList = ({
  subcategoryId,
  subCategories,
  venueList,
}: IUseFilteredVenueListProps): TOfferIndividualVenue[] => {
  const [filteredVenueList, setFilteredVenueList] =
    useState<TOfferIndividualVenue[]>(venueList)

  useEffect(() => {
    if (subcategoryId) {
      const subCategory = subCategories.find(s => s.id === subcategoryId)
      if (
        subCategory &&
        subCategory.onlineOfflinePlatform !== CATEGORY_STATUS.ONLINE_OR_OFFLINE
      ) {
        setFilteredVenueList(
          venueList.filter(v => {
            return subCategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
              ? v.isVirtual
              : !v.isVirtual
          })
        )
      }
    }
  }, [subcategoryId])

  return filteredVenueList
}

export default useFilteredVenueList
