import offerersSelector from '../offerers'
import state from './mockState01-2019'

describe('offerersSelector', () => {
  describe('when there is offerId and no mediationId', () => {
    it('should select the current recommendation corresponding to a mediation', () => {
      // given
      const expected = [
        {
          address: '21 RUE ALEXIS LEPERE',
          bic: null,
          city: 'Montreuil',
          dateCreated: '2019-01-10T16:36:58.161929Z',
          dateModifiedAtLastProvider: '2019-01-10T16:37:08.761267Z',
          firstThumbDominantColor: null,
          iban: null,
          id: 'AH4Q',
          idAtProviders: null,
          isActive: true,
          isValidated: true,
          lastProviderId: null,
          managedVenuesIds: ['AHUA', 'AHVA'],
          modelName: 'Offerer',
          nOffers: 0,
          name: 'LA MARBRERIE',
          postalCode: '93100',
          siren: '812182491',
          thumbCount: 0,
        },
        {
          address: '1 BD POISSONNIERE',
          bic: null,
          city: 'Paris',
          dateCreated: '2019-01-10T16:36:58.161929Z',
          dateModifiedAtLastProvider: '2019-01-10T16:37:08.710028Z',
          firstThumbDominantColor: null,
          iban: null,
          id: 'AH2A',
          idAtProviders: null,
          isActive: true,
          isValidated: true,
          lastProviderId: null,
          managedVenuesIds: ['AHPA', 'AHPQ'],
          modelName: 'Offerer',
          nOffers: 3,
          name: 'LE GRAND REX PARIS',
          postalCode: '75002',
          siren: '507633576',
          thumbCount: 0,
        },
      ]

      // when
      const result = offerersSelector(state)

      // then
      expect(result).toEqual(expected)
    })
  })
})
