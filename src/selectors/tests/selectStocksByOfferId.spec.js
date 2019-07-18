import selectStocksByOfferId from '../selectStocksByOfferId'

describe('src | selectors | selectStocksByOfferId', () => {
  it('should return an empty list of stock when there is no stock related to the offer selected', () => {
    // given
    const offerId = 'M4'
    const state = {
      data: {
        offers: [],
        stocks: [],
      },
    }

    // when
    const stocksToDisplay = selectStocksByOfferId(state, offerId)

    // then
    expect(stocksToDisplay).toStrictEqual([])
  })

  it('should return only stock related to the offer selected', () => {
    // given
    const offerId = 'M4'
    const state = {
      data: {
        offers: [
          {
            id: 'M4',
            isEvent: true,
            isThing: false,
          },
          {
            id: 'NE',
            isEvent: false,
            isThing: true,
          },
        ],
        stocks: [
          {
            id: 'MU',
            beginningDatetime: null,
            offerId: 'NE',
          },
          {
            id: 'MQ',
            beginningDatetime: new Date('2019-12-24 20:00:00'),
            offerId: 'M4',
          },
          {
            id: 'M9',
            beginningDatetime: new Date('2019-11-23 20:00:00'),
            offerId: 'M4',
          },
        ],
      },
    }

    // when
    const stocksToDisplay = selectStocksByOfferId(state, offerId)

    // then
    const stockListExpected = [
      {
        id: 'MQ',
        beginningDatetime: new Date('2019-12-24 20:00:00'),
        offerId: 'M4',
      },
      {
        id: 'M9',
        beginningDatetime: new Date('2019-11-23 20:00:00'),
        offerId: 'M4',
      },
    ]

    expect(stocksToDisplay).toStrictEqual(stockListExpected)
  })

  it('should return an empty list of stock when state is not initialized', () => {
    // given
    const offerId = 'M4'
    const state = {
      data: {},
    }

    // when
    const stocksToDisplay = selectStocksByOfferId(state, offerId)

    // then
    const stockListExpected = []
    expect(stocksToDisplay).toStrictEqual(stockListExpected)
  })
})
