import stockPatchSelector from '../stockPatch'

import mockStateForStockPatchTest from './mockStateForStockPatchTest'

describe('createOfferersSelector', () => {
  it('should select the global state', () => {
    // given
    const state = mockStateForStockPatchTest
    const stock = {
      available: 22,
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      bookingRecapSent: null,
      dateModified: '2019-03-07T10:40:07.318721Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
      eventOccurrenceId: null,
      groupSize: 1,
      id: 'MU',
      idAtProviders: null,
      isSoftDeleted: false,
      lastProviderId: null,
      modelName: 'Stock',
      offerId: 'UU',
      price: 17,
    }

    const offerId = 'UU'
    const eventOccurrenceId = undefined
    const managingOffererId = 'BA'

    // when
    const result = stockPatchSelector(
      state,
      stock,
      offerId,
      eventOccurrenceId,
      managingOffererId
    )
    const expected = {
      available: 22,
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      bookingRecapSent: null,
      dateModified: '2019-03-07T10:40:07.318721Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
      eventOccurrenceId: null,
      groupSize: 1,
      id: 'MU',
      idAtProviders: null,
      isSoftDeleted: false,
      lastProviderId: null,
      modelName: 'Stock',
      offerId: 'UU',
      offererId: 'BA',
      price: 17,
    }

    // then
    expect(result).toEqual(expected)
  })
})
