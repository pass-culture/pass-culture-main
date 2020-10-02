import { isOfferFromStockProvider } from '../localProvider'

describe('src | isOfferFromStockProvider', () => {
  describe('when offer is linked to a specific provider', () => {
    it('should return false if last provider is not in list', () => {
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
      expect(isOfferLibrairesGenerated).toBe(false)
    })

    it('should return true if provider is LesLibraires', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: {
          name: 'Leslibraires.fr',
        },
      }

      // when
      const isOfferLibrairesGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferLibrairesGenerated).toBe(true)
    })

    it('should return true if provider is TiteLive Stocks', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: {
          name: 'TiteLive Stocks (Epagine / Place des libraires.com)',
        },
      }

      // when
      const isOfferTiteLiveGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferTiteLiveGenerated).toBe(true)
    })

    it('should return true if provider is TiteLive Things', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: {
          name: 'TiteLive (Epagine / Place des libraires.com)',
        },
      }

      // when
      const isOfferTiteLiveGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferTiteLiveGenerated).toBe(true)
    })

    it('should return true if provider is Fnac', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: {
          name: 'Fnac',
        },
      }

      // when
      const isOfferFnacGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferFnacGenerated).toBe(true)
    })

    it('should return true if provider is Praxiel', () => {
      // given
      const offer = {
        id: 'AZER',
        lastProvider: {
          name: 'Praxiel',
        },
      }

      // when
      const isOfferPraxielGenerated = isOfferFromStockProvider(offer)

      // then
      expect(isOfferPraxielGenerated).toBe(true)
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
