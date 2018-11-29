import { getOfferTypeLabel } from '../offerItem'

describe('getOfferTypeLabel', () => {
  describe('when event exists', () => {
    it('should return event offer type label', () => {
      // given
      const event = { offerType: { label: 'Conférence — Débat — Dédicace' } }
      const thing = undefined

      // when
      const offerTypeLabel = getOfferTypeLabel(event, thing)

      // then
      expect(offerTypeLabel).toEqual('Conférence — Débat — Dédicace')
    })
  })

  describe('when thing exists', () => {
    it('should return thing offer type label', () => {
      // given
      const thing = { offerType: { label: 'Jeux (Biens physiques)' } }
      const event = undefined

      // when
      const offerTypeLabel = getOfferTypeLabel(event, thing)

      // then
      expect(offerTypeLabel).toEqual('Jeux (Biens physiques)')
    })
  })
})
