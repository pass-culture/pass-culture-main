import { getProviderInfo } from '../getProviderInfo'
import { PROVIDER_ICONS } from '../../../../utils/providers'

describe('src | getProviderInfo', () => {
  describe('when offer came from Tite live', () => {
    it('should return its icon and label', () => {
      // given
      const titeliveId = 'titelive stocks'

      // when
      const providerInfo = getProviderInfo(titeliveId)

      // then
      expect(providerInfo).toStrictEqual({
        id: 'titelive',
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live',
      })
    })
  })

  describe('when offer came from Allociné', () => {
    it('should return its icon and label', () => {
      // given
      const allocineId = 'allociné'

      // when
      const providerInfo = getProviderInfo(allocineId)

      // then
      expect(providerInfo).toStrictEqual({
        id: 'allociné',
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné',
      })
    })
  })

  describe('when offer came from Libraires', () => {
    it('should return its icon and label', () => {
      // given
      const leslibrairesId = 'leslibraires.fr'

      // when
      const providerInfo = getProviderInfo(leslibrairesId)

      // then
      expect(providerInfo).toStrictEqual({
        id: 'leslibraires.fr',
        icon: PROVIDER_ICONS['LibrairesStocks'],
        name: 'Leslibraires.fr',
      })
    })
  })

  describe('when offer came from Fnac', () => {
    it('should return its icon and label', () => {
      // given
      const fnacId = 'fnac'

      // when
      const providerInfo = getProviderInfo(fnacId)

      // then
      expect(providerInfo).toStrictEqual({
        id: 'fnac',
        icon: PROVIDER_ICONS['FnacStocks'],
        name: 'Fnac',
      })
    })
  })

  describe('when offer came from Praxiel', () => {
    it('should return its icon and label', () => {
      // given
      const praxielId = 'praxiel'

      // when
      const providerInfo = getProviderInfo(praxielId)

      // then
      expect(providerInfo).toStrictEqual({
        id: 'praxiel',
        icon: PROVIDER_ICONS['PraxielStocks'],
        name: 'Praxiel',
      })
    })
  })
})
