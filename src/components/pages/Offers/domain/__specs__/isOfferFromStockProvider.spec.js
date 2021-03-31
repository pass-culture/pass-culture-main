import { isOfferFromStockProvider } from '../localProvider'

describe('src | isOfferFromStockProvider', () => {
  describe('when offer is linked to a provider', () => {
    it('should return true', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: {
          name: 'Anyotherprovider',
        },
      }

      // when
      const isOfferLibrairesGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferLibrairesGenerated).toBe(true)
    })
  })

  describe('when offer is not linked to a specific provider', () => {
    it('should return false if last provider is null', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: null,
      }

      // when
      const isOfferLibrairesGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferLibrairesGenerated).toBe(false)
    })

    it('should return false if last provider is undefined', () => {
      // given
      const offer = {
        id: 'AZER',
      }

      // when
      const isOfferLibrairesGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferLibrairesGenerated).toBe(false)
    })
  })
})
