import { useGetOffererNames } from 'core/Offerers/adapters'
import { TOffererName } from 'core/Offerers/types'
import { useGetCategories, useGetOfferIndividual } from 'core/Offers/adapters'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { useGetOfferIndividualVenues } from 'core/Venue'
import { TOfferIndividualVenue } from 'core/Venue/types'

interface IUseGetDataSuccessPayload {
  offer: IOfferIndividual
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
}

interface IUseAdapterSuccess {
  data: IUseGetDataSuccessPayload
  isLoading: false
  loadingError?: undefined
}

interface IUseAdapterFailure {
  data?: undefined
  isLoading: false
  loadingError: string
}

const useGetData = (
  offerId: string
): IUseGetDataLoading | IUseAdapterSuccess | IUseAdapterFailure => {
  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
  } = useGetOfferIndividual(offerId)
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
      loadingError:
        loadingError?.message ||
        'Une erreur est survenu lors de la récupération des données',
    }
  }

  return {
    isLoading: false,
    data: {
      offer,
      offererNames,
      venueList,
      categoriesData,
    },
  }
}

export default useGetData
