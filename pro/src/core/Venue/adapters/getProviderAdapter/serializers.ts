import { ProviderResponse } from 'apiClient/v1'

export const serializeProvidersApi = (providers: any): ProviderResponse[] => {
  return providers.map((provider: any) => ({
    enabledForPro: provider.enabledForPro,
    id: provider.id,
    isActive: provider.isActive,
    name: provider.name,
  }))
}
