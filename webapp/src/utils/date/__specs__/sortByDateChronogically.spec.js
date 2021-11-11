import moment from 'moment'
import { sortByDateChronologically } from '../sortByDateChronologically'

describe('sortByDateChronologically', () => {
  let firstDate
  let middleDate
  let lastDate

  beforeEach(() => {
    firstDate = moment(new Date('2001-09-10T08:00:00Z').toISOString())
    middleDate = moment(new Date('2015-09-10T08:00:00Z').toISOString())
    lastDate = moment(new Date('2020-09-10T08:00:00Z').toISOString())
  })

  it('should sort by date asc', () => {
    // given
    const stocks = [
      {
        id: 3,
        beginningDatetime: lastDate,
      },
      {
        id: 1,
        beginningDatetime: firstDate,
      },
      {
        id: 2,
        beginningDatetime: middleDate,
      },
    ]

    // when
    const expected = sortByDateChronologically()(stocks)

    // then
    expect(expected).toStrictEqual([
      {
        beginningDatetime: expect.any(Object),
        id: 1,
      },
      {
        beginningDatetime: expect.any(Object),
        id: 2,
      },
      {
        beginningDatetime: expect.any(Object),
        id: 3,
      },
    ])
  })

  describe('when there is no beginningDatetime', () => {
    it('should sort stocks and put stocks whithout beginningDatetime at the end when empty stock is first', () => {
      // given
      const stocks = [
        {
          id: 4,
          beginningDatetime: null,
        },
        {
          id: 3,
          beginningDatetime: lastDate,
        },
        {
          id: 2,
          beginningDatetime: middleDate,
        },
        {
          id: 1,
          beginningDatetime: firstDate,
        },
      ]

      // when
      const expected = sortByDateChronologically()(stocks)

      // then
      expect(expected).toStrictEqual([
        {
          beginningDatetime: expect.any(Object),
          id: 1,
        },
        {
          beginningDatetime: expect.any(Object),
          id: 2,
        },
        {
          beginningDatetime: expect.any(Object),
          id: 3,
        },
        {
          beginningDatetime: null,
          id: 4,
        },
      ])
    })

    it('should sort stocks and put stocks whithout beginningDatetime at the end when empty stock is in the middle', () => {
      // given
      const stocks = [
        {
          id: 3,
          beginningDatetime: lastDate,
        },
        {
          id: 4,
          beginningDatetime: null,
        },
        {
          id: 2,
          beginningDatetime: middleDate,
        },
        {
          id: 1,
          beginningDatetime: firstDate,
        },
      ]

      // when
      const expected = sortByDateChronologically()(stocks)

      // then
      expect(expected).toStrictEqual([
        {
          beginningDatetime: expect.any(Object),
          id: 1,
        },
        {
          beginningDatetime: expect.any(Object),
          id: 2,
        },
        {
          beginningDatetime: expect.any(Object),
          id: 3,
        },
        {
          beginningDatetime: null,
          id: 4,
        },
      ])
    })

    it('should sort stocks and put stocks whithout beginningDatetime at the end when empty stock is at the end', () => {
      // given
      const stocks = [
        {
          id: 3,
          beginningDatetime: lastDate,
        },
        {
          id: 2,
          beginningDatetime: middleDate,
        },
        {
          id: 1,
          beginningDatetime: firstDate,
        },
        {
          id: 4,
          beginningDatetime: null,
        },
      ]

      // when
      const expected = sortByDateChronologically()(stocks)

      // then
      expect(expected).toStrictEqual([
        {
          beginningDatetime: expect.any(Object),
          id: 1,
        },
        {
          beginningDatetime: expect.any(Object),
          id: 2,
        },
        {
          beginningDatetime: expect.any(Object),
          id: 3,
        },
        {
          beginningDatetime: null,
          id: 4,
        },
      ])
    })
  })
})
