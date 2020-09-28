import { getProviderInfo } from '../getProviderInfo'
import { PROVIDER_ICONS } from '../../../../utils/providers'

describe('src | getProviderInfo', () => {
  describe('when offer came from Tite live', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isAllocine = false
      const isLibraires = false
      const isTiteLive = true

      // when
      const providerInfo = getProviderInfo(isTiteLive, isAllocine, isLibraires)

      // then
      expect(providerInfo).toStrictEqual({
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live',
      })
    })
  })

  describe('when offer came from Allociné', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isAllocine = true
      const isLibraires = false
      const isTiteLive = false

      // when
      const providerInfo = getProviderInfo(isTiteLive, isAllocine, isLibraires)

      // then
      expect(providerInfo).toStrictEqual({
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné',
      })
    })
  })

  describe('when offer came from Libraires', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isAllocine = false
      const isLibraires = true
      const isTiteLive = false

      // when
      const providerInfo = getProviderInfo(isTiteLive, isAllocine, isLibraires)

      // then
      expect(providerInfo).toStrictEqual({
        icon: PROVIDER_ICONS['LibrairesStocks'],
        name: 'Leslibraires.fr',
      })
    })
  })

  describe('when offer came from Fnac', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isAllocine = false
      const isLibraires = false
      const isTiteLive = false
      const isFnac = true

      // when
      const providerInfo = getProviderInfo(isTiteLive, isAllocine, isLibraires, isFnac)

      // then
      expect(providerInfo).toStrictEqual({
        icon: PROVIDER_ICONS['FnacStocks'],
        name: 'Fnac',
      })
    })
  })
})
