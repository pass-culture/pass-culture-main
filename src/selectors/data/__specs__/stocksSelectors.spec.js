import { selectIsEnoughStockForOfferDuo, selectIsStockDuo } from '../stocksSelectors'

describe('selectIsEnoughStockForOfferDuo', () => {
  it('should return true when there is stock with more than two remainingQuantityOrUnlimited', () => {
    // given
    const state = {
      data: {
        stocks: [
          {
            offerId: 'AAAA',
            remainingQuantityOrUnlimited: 2,
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
            remainingQuantityOrUnlimited: 'unlimited',
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

  it('should return false when there is no stock with more than two remainingQuantityOrUnlimited', () => {
    // given
    const state = {
      data: {
        stocks: [
          {
            offerId: 'AAAA',
            remainingQuantityOrUnlimited: 1,
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
            remainingQuantityOrUnlimited: 5,
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
  it('should be duo if stock remainingQuantityOrUnlimited 2 or more and on an offer duo', () => {
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
            remainingQuantityOrUnlimited: 5,
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
            remainingQuantityOrUnlimited: 'unlimited',
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

  it('should not be duo if there less than 2 remainingQuantityOrUnlimited', () => {
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
            remainingQuantityOrUnlimited: 1,
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
            remainingQuantityOrUnlimited: 2,
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
