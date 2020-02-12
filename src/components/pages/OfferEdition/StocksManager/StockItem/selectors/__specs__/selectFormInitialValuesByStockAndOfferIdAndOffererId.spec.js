import selectFormInitialValuesByStockAndOfferIdAndOffererId from '../selectFormInitialValuesByStockAndOfferIdAndOffererId'

describe('components | OfferEdition | selectFormInitialValuesByStockAndOfferIdAndOffererId', () => {
  it('should select the global state', () => {
    // given
    const offerId = 'UU'
    const managingOffererId = 'BA'
    const stock = {
      available: 22,
      beginningDatetime: undefined,
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
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      id: 'MU',
      offerId: 'UU',
      offererId: 'BA',
      price: 17,
    }

    // then
    expect(result).toStrictEqual(expected)
  })

  it('should select the global state when pro user does not provide booking limit date time and offer is an event', () => {
    // given
    const offerId = 'AB'
    const managingOffererId = 'CD'
    const stock = {
      available: 2,
      beginningDatetime: '2020-02-06T10:37:12.683Z',
      bookingLimitDatetime: null,
      bookingRecapSent: null,
      dateModified: '2019-03-07T10:40:07.318721Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
      endDatetime: '2020-02-06T11:37:12.683Z',
      groupSize: 1,
      id: 'MU',
      idAtProviders: null,
      isSoftDeleted: false,
      lastProviderId: null,
      modelName: 'Stock',
      offerId: 'AB',
      price: 10,
    }
    const state = {
      data: {
        offers: [{ id: offerId, isThing: true, isEvent: true }],
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

    // then
    const expected = {
      available: 2,
      beginningDatetime: '2020-02-06T10:37:12.683Z',
      bookingLimitDatetime: '',
      endDatetime: '2020-02-06T11:37:12.683Z',
      id: 'MU',
      offerId: 'AB',
      offererId: 'CD',
      price: 10,
    }
    expect(result).toStrictEqual(expected)
  })
})
