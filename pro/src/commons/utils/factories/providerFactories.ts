import type { GetOfferLastProviderResponseModelV2 } from '@/apiClient/v1'

export const getOfferLastProvider = (
  customOfferLastProvider: Partial<GetOfferLastProviderResponseModelV2> = {}
): GetOfferLastProviderResponseModelV2 => {
  return {
    name: 'Le nom du dernier fournisseur',
    ...customOfferLastProvider,
  }
}
