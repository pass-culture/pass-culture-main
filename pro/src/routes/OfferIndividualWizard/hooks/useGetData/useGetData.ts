import { useGetOffererNames } from 'core/Offerers/adapters'
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

interface IUseGetDataSuccessPayload {
  offer: IOfferIndividual | undefined
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categoriesData: {
    categories: IOfferCategory[]
    subCategories: IOfferSubCategory[]
  }
}

interface IUseGetDataLoading {
  data?: undefined
  isLoading: true
  loadingError?: undefined
  reloadOffer?: undefined
}

interface IUseAdapterSuccess {
  data: IUseGetDataSuccessPayload
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

const useGetData = (
  offerId?: string
): IUseGetDataLoading | IUseAdapterSuccess | IUseAdapterFailure => {
  const {
    data: offererNames,
    isLoading: offererNamesIsLoading,
    error: offererNamesError,
  } = useGetOffererNames()
  const {
    data: venueList,
    isLoading: venueListIsLoading,
    error: venueListError,
  } = useGetOfferIndividualVenues()
  const {
    data: categoriesData,
    isLoading: categoriesIsLoading,
    error: categoriesError,
  } = useGetCategories()

  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
    reloadOffer,
  } = useGetOffer(offerId)

  if (
    offererNamesIsLoading === true ||
    venueListIsLoading === true ||
    categoriesIsLoading === true ||
    offerIsLoading === true
  ) {
    return { isLoading: true }
  }

  if (
    offererNamesError !== undefined ||
    venueListError !== undefined ||
    categoriesError !== undefined ||
    offerError !== undefined
  ) {
    const loadingError = [
      offererNamesError,
      venueListError,
      categoriesError,
      offerError,
    ].find(error => error !== undefined)

    return {
      isLoading: false,
      loadingError: loadingError?.message || GET_DATA_ERROR_MESSAGE,
    }
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

export default useGetData
