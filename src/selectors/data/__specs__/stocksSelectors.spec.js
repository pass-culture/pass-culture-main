import moment from 'moment'

import {
  selectBookables,
  selectBookablesWithoutDateNotAvailable,
  selectIsEnoughStockForOfferDuo,
  selectIsStockDuo,
} from '../stocksSelectors'

describe('selectIsEnoughStockForOfferDuo', () => {
  it('should return true when there is stock with more than two remainingQuantity', () => {
    // given
    const state = {
      data: {
        stocks: [
          {
            offerId: 'AAAA',
            remainingQuantity: 2,
          },
        ],
      },
    }

    const offerId = 'AAAA'

    // when
    const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

    // then
    expect(isEnoughStockForOfferDuo).toBe(true)
  })

  it('should return true when there is unlimited stock', () => {
    // given
    const state = {
      data: {
        stocks: [
          {
            offerId: 'AAAA',
            remainingQuantity: 'unlimited',
          },
        ],
      },
    }

    const offerId = 'AAAA'

    // when
    const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

    // then
    expect(isEnoughStockForOfferDuo).toBe(true)
  })

  it('should return false when there is no stock with more than two remainingQuantity', () => {
    // given
    const state = {
      data: {
        stocks: [
          {
            offerId: 'AAAA',
            remainingQuantity: 1,
          },
        ],
      },
    }

    const offerId = 'AAAA'

    // when
    const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

    // then
    expect(isEnoughStockForOfferDuo).toBe(false)
  })

  it('should return false when there is no match between stock and offer', () => {
    // given
    const state = {
      data: {
        stocks: [
          {
            offerId: 'AAAA',
            remainingQuantity: 5,
          },
        ],
      },
    }

    const offerId = 'BBBB'

    // when
    const isEnoughStockForOfferDuo = selectIsEnoughStockForOfferDuo(state, offerId)

    // then
    expect(isEnoughStockForOfferDuo).toBe(false)
  })
})

describe('selectIsStockDuo', () => {
  it('should be duo if stock remainingQuantity 2 or more and on an offer duo', () => {
    // given
    const state = {
      data: {
        offers: [
          {
            id: 'O1',
            isDuo: true,
          },
        ],
        stocks: [
          {
            id: 'S1',
            offerId: 'O1',
            remainingQuantity: 5,
          },
        ],
      },
    }

    const offerId = 'O1'
    const stockId = 'S1'

    // when
    const isStockDuo = selectIsStockDuo(state, stockId, offerId)

    // then
    expect(isStockDuo).toBe(true)
  })

  it('should be duo if stock unlimited and on an offer duo', () => {
    // given
    const state = {
      data: {
        offers: [
          {
            id: 'O1',
            isDuo: true,
          },
        ],
        stocks: [
          {
            id: 'S1',
            offerId: 'O1',
            remainingQuantity: 'unlimited',
          },
        ],
      },
    }

    const offerId = 'O1'
    const stockId = 'S1'

    // when
    const isStockDuo = selectIsStockDuo(state, stockId, offerId)

    // then
    expect(isStockDuo).toBe(true)
  })

  it('should not be duo if there less than 2 remainingQuantity', () => {
    // given
    const state = {
      data: {
        offers: [
          {
            id: 'O1',
            isDuo: true,
          },
        ],
        stocks: [
          {
            id: 'S1',
            offerId: 'O1',
            remainingQuantity: 1,
          },
        ],
      },
    }

    const offerId = 'O1'
    const stockId = 'S1'

    // when
    const isStockDuo = selectIsStockDuo(state, stockId, offerId)

    // then
    expect(isStockDuo).toBe(false)
  })

  it('should not be duo if his offer is not duo', () => {
    // given
    const state = {
      data: {
        offers: [
          {
            id: 'O1',
            isDuo: false,
          },
        ],
        stocks: [
          {
            id: 'S1',
            offerId: 'O1',
            remainingQuantity: 2,
          },
        ],
      },
    }
    const offerId = 'O1'
    const stockId = 'S1'

    // when
    const isStockDuo = selectIsStockDuo(state, stockId, offerId)

    // then
    expect(isStockDuo).toBe(false)
  })
})

describe('selectBookables', () => {
  it('should return empty array when nothing is found', () => {
    // given
    const state = {
      data: {
        bookings: [],
        stocks: [],
      },
    }
    const offer = {}

    // when
    const result = selectBookables(state, offer)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return stocks with completed data', () => {
    // given
    jest.spyOn(Date, 'now').mockImplementation(() => '2000-01-01T20:00:00Z')
    const state = {
      data: {
        bookings: [
          {
            stockId: 'AB',
          },
        ],
        stocks: [
          {
            id: 'AB',
            offerId: 'AA',
            beginningDatetime: moment(),
          },
        ],
      },
    }
    const offer = {
      id: 'AA',
    }

    // when
    const result = selectBookables(state, offer)

    // then
    expect(result).toStrictEqual([
      {
        __modifiers__: ['selectBookables'],
        beginningDatetime: expect.any(Object),
        humanBeginningDate: 'Saturday 01/01/2000 à 21:00',
        id: 'AB',
        offerId: 'AA',
        userHasAlreadyBookedThisDate: true,
        userHasCancelledThisDate: false,
      },
    ])
  })
})

describe('selectBookablesWithoutDateNotAvailable', () => {
  it('should return stocks with remaining quantity or unlimited', () => {
    // given
    const state = {
      data: {
        bookings: [],
        stocks: [
          {
            id: 'AB',
            offerId: 'ZZ',
            remainingQuantity: 0,
          },
          {
            id: 'AC',
            offerId: 'AA',
            remainingQuantity: 1,
          },
          {
            id: 'AD',
            offerId: 'AA',
            remainingQuantity: 'unlimited',
          },
        ],
      },
    }
    const offer = {
      id: 'AA',
    }

    // when
    const result = selectBookablesWithoutDateNotAvailable(state, offer)

    // then
    expect(result).toStrictEqual([
      {
        __modifiers__: ['selectBookables'],
        id: 'AC',
        offerId: 'AA',
        userHasAlreadyBookedThisDate: false,
        userHasCancelledThisDate: false,
        remainingQuantity: 1,
      },
      {
        __modifiers__: ['selectBookables'],
        id: 'AD',
        offerId: 'AA',
        userHasAlreadyBookedThisDate: false,
        userHasCancelledThisDate: false,
        remainingQuantity: 'unlimited',
      },
    ])
  })
})
