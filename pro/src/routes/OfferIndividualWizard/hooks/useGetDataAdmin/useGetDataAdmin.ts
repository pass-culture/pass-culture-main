import { TOffererName } from 'core/Offerers/types'
import { useGetCategories } from 'core/Offers/adapters'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useGetOfferIndividualVenues } from 'core/Venue'
import { TOfferIndividualVenue } from 'core/Venue/types'

import { useGetOffer } from '../useGetOffer'

interface IuseGetDataAdminSuccessPayload {
  offer: IOfferIndividual | undefined
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categoriesData: {
    categories: IOfferCategory[]
    subCategories: IOfferSubCategory[]
  }
}

interface IuseGetDataAdminLoading {
  data?: undefined
  isLoading: true
  loadingError?: undefined
  reloadOffer?: undefined
}

interface IUseAdapterSuccess {
  data: IuseGetDataAdminSuccessPayload
  isLoading: false
  loadingError?: undefined
  reloadOffer: () => void
}

interface IUseAdapterFailure {
  data?: undefined
  isLoading: false
  loadingError: string
  reloadOffer?: undefined
}

const useGetDataAdmin = (
  offerId?: string,
  offererId?: string
): IuseGetDataAdminLoading | IUseAdapterSuccess | IUseAdapterFailure => {
  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
    reloadOffer,
  } = useGetOffer(offerId)
  const {
    data: venueList,
    isLoading: venueListIsLoading,
    error: venueListError,
  } = useGetOfferIndividualVenues({
    isAdmin: true,
    offererId: offer ? offer.offererId : offererId,
  })
  const {
    data: categoriesData,
    isLoading: categoriesIsLoading,
    error: categoriesError,
  } = useGetCategories()

  if (
    venueListIsLoading === true ||
    categoriesIsLoading === true ||
    offerIsLoading === true
  ) {
    return { isLoading: true }
  }

  if (
    venueListError !== undefined ||
    categoriesError !== undefined ||
    offerError !== undefined
  ) {
    const loadingError = [venueListError, categoriesError, offerError].find(
      error => error !== undefined
    )

    return {
      isLoading: false,
      loadingError: loadingError?.message || GET_DATA_ERROR_MESSAGE,
    }
  }

  const offererNames: TOffererName[] = []
  if (offer) {
    offererNames.push({
      id: offer.offererId,
      name: offer.offererName,
    })
  }

  return {
    isLoading: false,
    reloadOffer,
    data: {
      offer,
      offererNames,
      venueList,
      categoriesData,
    },
  }
}

export default useGetDataAdmin
