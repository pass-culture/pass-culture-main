import { PROVIDER_ICONS } from '../../../utils/providers'

export const getProviderInfo = (isTitelive, isAllocine) => {
  const defaultCase = !isTitelive && !isAllocine
  switch (true) {
    case isAllocine:
      return {
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné'
      }
    case isTitelive:
    case defaultCase:
      return {
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live'
      }
  }
}
