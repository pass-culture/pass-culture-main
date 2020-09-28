import { PROVIDER_ICONS } from '../../../utils/providers'

export const getProviderInfo = (isTitelive, isAllocine, isLibraires, isFnac) => {
  switch (true) {
    case isAllocine:
      return {
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné',
      }
    case isLibraires:
      return {
        icon: PROVIDER_ICONS['LibrairesStocks'],
        name: 'Leslibraires.fr',
      }
    case isTitelive:
      return {
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live',
      }
    case isFnac:
      return {
        icon: PROVIDER_ICONS['FnacStocks'],
        name: 'Fnac',
      }
    default:
      return {
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live',
      }
  }
}
