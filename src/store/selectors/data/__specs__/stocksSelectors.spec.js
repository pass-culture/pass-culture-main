import { selectStocksByOfferId } from '../stocksSelectors'

describe('src | selectors | selectStocksByOfferId', () => {
  it('should return an empty array when there is no stock related to the offer id', () => {
    // given
    const offerId = 'M4'
    const state = {
      data: {
        offers: [],
        stocks: [],
      },
    }

    // when
    const result = selectStocksByOfferId(state, offerId)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return an array of stocks related to given offer id', () => {
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
    const result = selectStocksByOfferId(state, offerId)

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

    expect(result).toStrictEqual(stockListExpected)
  })
})
