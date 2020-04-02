import { PROVIDER_ICONS } from '../../../utils/providers'

export const getProviderInfo = (isTitelive, isAllocine, isLibraires) => {
  const defaultCase = !isTitelive && !isAllocine && !isLibraires
  switch (true) {
    case isAllocine:
      return {
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné'
      }
    case isLibraires:
      return {
        icon: PROVIDER_ICONS['LibrairesStocks'],
        name: 'Leslibraires.fr'
      }
    case isTitelive:
    case defaultCase:
      return {
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live'
      }
  }
}
