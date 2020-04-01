import selectFormInitialValuesByStockAndOfferIdAndOffererId from '../selectFormInitialValuesByStockAndOfferIdAndOffererId'

describe('src | components | pages | Offer | StocksManager | StockItem | selectors | selectFormInitialValuesByStockAndOfferIdAndOffererId', () => {
  it('should select the global state', () => {
    // given
    const offerId = 'UU'
    const managingOffererId = 'BA'
    const stock = {
      beginningDatetime: undefined,
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      bookingRecapSent: null,
      dateModified: '2019-03-07T10:40:07.318721Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
      id: 'MU',
      idAtProviders: null,
      isSoftDeleted: false,
      lastProviderId: null,
      modelName: 'Stock',
      offerId: 'UU',
      price: 17,
      quantity: 22,
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
      bookingLimitDatetime: '2019-03-13T23:00:00Z',
      id: 'MU',
      offerId: 'UU',
      offererId: 'BA',
      price: 17,
      quantity: 22,
    }

    // then
    expect(result).toStrictEqual(expected)
  })

  it('should select the global state when pro user does not provide booking limit date time and offer is an event', () => {
    // given
    const offerId = 'AB'
    const managingOffererId = 'CD'
    const stock = {
      beginningDatetime: '2020-02-06T10:37:12.683Z',
      bookingLimitDatetime: null,
      bookingRecapSent: null,
      dateModified: '2019-03-07T10:40:07.318721Z',
      dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
      id: 'MU',
      idAtProviders: null,
      isSoftDeleted: false,
      lastProviderId: null,
      modelName: 'Stock',
      offerId: 'AB',
      price: 10,
      quantity: 2,
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
      beginningDatetime: '2020-02-06T10:37:12.683Z',
      bookingLimitDatetime: '',
      id: 'MU',
      offerId: 'AB',
      offererId: 'CD',
      price: 10,
      quantity: 2,
    }
    expect(result).toStrictEqual(expected)
  })
})
