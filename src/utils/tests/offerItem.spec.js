import { getOfferTypeLabel } from '../offerItem'

describe('getOfferTypeLabel', () => {
  describe('when event exists', () => {
    it('should return event offer type label', () => {
      // given
      const product = { offerType: { proLabel: 'Conférence — Débat — Dédicace' } }

      // when
      const offerTypeLabel = getOfferTypeLabel(product)

      // then
      expect(offerTypeLabel).toStrictEqual('Conférence — Débat — Dédicace')
    })
  })

  describe('when thing exists', () => {
    it('should return thing offer type label', () => {
      // given
      const product = { offerType: { proLabel: 'Jeux (Biens physiques)' } }

      // when
      const offerTypeLabel = getOfferTypeLabel(product)

      // then
      expect(offerTypeLabel).toStrictEqual('Jeux (Biens physiques)')
    })
  })
})
