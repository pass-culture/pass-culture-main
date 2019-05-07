import selectOffererById from '../selectOffererById'
import state from './mockState'

describe('selectOffererById', () => {
  it('should retrieve offerer from state when id is given', () => {
    // given
    const expected = {
      address: 'RUE DES SAPOTILLES',
      bic: 'QSDFGH8Z566',
      city: 'Cayenne',
      dateCreated: '2019-05-06T09:12:46.278743Z',
      dateModifiedAtLastProvider: '2019-05-06T09:13:08.458343Z',
      firstThumbDominantColor: null,
      iban: 'FR7630001007941234567890185',
      id: '4Q',
      idAtProviders: null,
      isActive: true,
      isValidated: true,
      lastProviderId: null,
      modelName: 'Offerer',
      nOffers: 5,
      name: 'Bar des amis',
      postalCode: '97300',
      siren: '222222233',
      thumbCount: 0,
    }
    const offererId = '4Q'

    // when
    const result = selectOffererById(state, offererId)

    // then
    expect(result).toEqual(expected)
  })
})
