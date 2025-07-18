import { GetOfferLastProviderResponseModel } from 'apiClient/v1'

export const getOfferLastProvider = (
  customOfferLastProvider: Partial<GetOfferLastProviderResponseModel> = {}
): GetOfferLastProviderResponseModel => {
  return {
    name: 'Le nom du dernier fournisseur',
    ...customOfferLastProvider,
  }
}
