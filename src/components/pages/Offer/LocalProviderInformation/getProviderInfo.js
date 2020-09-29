import { PROVIDER_ICONS } from '../../../utils/providers'

export const getProviderInfo = providerName => {
  const providers = [
    {
      id: 'allociné',
      icon: PROVIDER_ICONS['AllocineStocks'],
      name: 'Allociné',
    },
    {
      id: 'leslibraires.fr',
      icon: PROVIDER_ICONS['LibrairesStocks'],
      name: 'Leslibraires.fr',
    },
    {
      id: 'titelive',
      icon: PROVIDER_ICONS['TiteLiveStocks'],
      name: 'Tite Live',
    },
    {
      id: 'fnac',
      icon: PROVIDER_ICONS['FnacStocks'],
      name: 'Fnac',
    },
  ]

  return providers.find(providerInfo => providerName.startsWith(providerInfo.id))
}
