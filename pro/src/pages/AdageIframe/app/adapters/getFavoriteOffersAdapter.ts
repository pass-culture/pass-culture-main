import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { Adapter, AdapterFailure } from 'pages/AdageIframe/app/types'

type GetFavoriteOffersAdapter = Adapter<
  void,
  (CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel)[],
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: null,
}

export const getFavoriteOffersAdapter: GetFavoriteOffersAdapter = async () => {
  try {
    const favoriteOffersResponse = await apiAdage.getCollectiveFavorites()

    const favoriteOfferTemplatesResponse: CollectiveOfferTemplateResponseModel[] =
      (favoriteOffersResponse?.favoritesTemplate ?? []).map((offer) => ({
        ...offer,
        isTemplate: true,
      }))

    const favoriteOffer: CollectiveOfferResponseModel[] = (
      favoriteOffersResponse?.favoritesOffer ?? []
    ).map((offer) => ({ ...offer, isTemplate: false }))

    return {
      isOk: true,
      message: null,
      payload: [...favoriteOfferTemplatesResponse, ...favoriteOffer],
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}
