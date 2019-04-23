import selectFormInitialValuesByStockAndOfferIdAndOffererId from '../selectFormInitialValuesByStockAndOfferIdAndOffererId'

describe('createOfferersSelector', () => {
  it('should select the global state', () => {
    // given
    const offerId = 'UU'
    const managingOffererId = 'BA'
    const stock = {
      available: 22,
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      bookingRecapSent: null,
      dateModified: '2019-03-07T10:40:07.318721Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
      groupSize: 1,
      id: 'MU',
      idAtProviders: null,
      isSoftDeleted: false,
      lastProviderId: null,
      modelName: 'Stock',
      offerId: 'UU',
      price: 17,
    }
    const state = {
      data: {
        offers: [{ id: offerId, isThing: true, isEvent: false }],
        stocks: [stock],
      },
    }

    // when
    const result = selectFormInitialValuesByStockAndOfferIdAndOffererId(
      state,
      stock,
      offerId,
      managingOffererId
    )
    const expected = {
      available: 22,
      beginningDatetime: undefined,
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      endDatetime: undefined,
      id: 'MU',
      offerId: 'UU',
      offererId: 'BA',
      price: 17,
    }

    // then
    expect(result).toEqual(expected)
  })
})
