import type { GetOfferLastProviderResponseModel } from '@/apiClient/v1/new'

export const getOfferLastProvider = (
  customOfferLastProvider: Partial<GetOfferLastProviderResponseModel> = {}
): GetOfferLastProviderResponseModel => {
  return {
    name: 'Le nom du dernier fournisseur',
    ...customOfferLastProvider,
  }
}
