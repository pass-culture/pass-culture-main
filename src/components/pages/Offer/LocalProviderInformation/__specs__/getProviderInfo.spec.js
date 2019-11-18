import { getProviderInfo } from '../getProviderInfo'
import { PROVIDER_ICONS } from '../../../../utils/providers'

describe('src | components | pages | Offer | LocalProviderInformation | getProviderInfo', () => {
  describe('when offer came from Tite live', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isTiteLive = true
      const isAllocine = false

      // when then
      expect(getProviderInfo(isTiteLive, isAllocine)).toStrictEqual({
        icon: PROVIDER_ICONS['TiteLiveStocks'],
        name: 'Tite Live'
      })
    })
  })

  describe('when offer came from Allociné', () => {
    it('should compute a provider info object accordingly', () => {
      // given
      const isTiteLive = false
      const isAllocine = true

      // when then
      expect(getProviderInfo(isTiteLive, isAllocine)).toStrictEqual({
        icon: PROVIDER_ICONS['AllocineStocks'],
        name: 'Allociné'
      })
    })
  })
})
