import { getProviderInfo } from '../getProviderInfo'
import { PROVIDER_ICONS } from '../../../../utils/providers'

describe('components | OfferEdition | getProviderInfo', () => {
  describe('when offer came from Tite live', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isTiteLive = true
      const isAllocine = false

      // when
      const providerInfo = getProviderInfo(isTiteLive, isAllocine)

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
      const isTiteLive = false
      const isAllocine = true

      // when
      const providerInfo = getProviderInfo(isTiteLive, isAllocine)

      // then
      expect(providerInfo).toStrictEqual({
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné',
      })
    })
  })
})
