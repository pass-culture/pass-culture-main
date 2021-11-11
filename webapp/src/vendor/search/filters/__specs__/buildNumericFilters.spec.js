import mockdate from 'mockdate'
import { DATE_FILTER } from '../../../../components/pages/search/Filters/filtersEnums'
import { AppSearchFields } from '../../constants'

import { buildNumericFilters } from '../buildNumericFilters'

const selectedDate = new Date(2021, 4, 5, 9, 30)

jest.mock('../../../../components/pages/search/utils/date/time')

describe('buildNumericFilters', () => {
  beforeEach(() => {
    mockdate.set(new Date('2021-07-01T02:03:04'))
    jest.clearAllMocks()
  })

  describe('offer price', () => {
    it('should not filter when no price range is specified and offer is not free', () => {
      const params = { offerIsFree: false, priceRange: null }
      expect(buildNumericFilters(params)).toStrictEqual([
        { [AppSearchFields.prices]: { to: 30000 } },
      ])
    })

    it('should filter prices when offer is free even when priceRange is provided', () => {
      const params = { offerIsFree: true, priceRange: [0, 300] }
      expect(buildNumericFilters(params)).toStrictEqual([{ [AppSearchFields.prices]: { to: 1 } }])
    })

    it('should filter prices when price range is provided and offer is not free', () => {
      const params = { offerIsFree: false, priceRange: [20, 50] }
      expect(buildNumericFilters(params)).toStrictEqual([
        { [AppSearchFields.prices]: { from: 2000, to: 5000 } },
      ])
    })

    it('should filter prices with max price when price range is provided and offer is not free', () => {
      const params = { offerIsFree: false, priceRange: [20, 500] }
      expect(buildNumericFilters(params)).toStrictEqual([
        { [AppSearchFields.prices]: { from: 2000, to: 30000 } },
      ])
    })
  })

  describe('offer is new', () => {
    it('should fetch with no numericFilters when offerIsNew is false', () => {
      const filters = buildNumericFilters({ offerIsNew: false })
      expect(filters).toStrictEqual([{ [AppSearchFields.prices]: { to: 30000 } }])
    })

    it('should fetch with numericFilters when offerIsNew is true', () => {
      const filters = buildNumericFilters({ offerIsNew: true })
      expect(filters).toStrictEqual([
        { [AppSearchFields.prices]: { to: 30000 } },
        {
          [AppSearchFields.stocks_date_created]: {
            from: '2021-06-16T02:05:00.000Z',
            to: '2021-07-01T02:05:00.000Z',
          },
        },
      ])
    })
  })

  describe('date', () => {
    describe('by date only', () => {
      const startOfDay = '2021-05-05T00:00:00.000Z'
      const from = '2021-05-05T09:30:00.000Z'
      const endOfDay = '2021-05-05T23:59:59.000Z'
      const endOfWeek = '2021-05-09T23:59:59.000Z'
      const startNextWeekEnd = '2021-05-08T00:00:00.000Z'

      it('should fetch with date filter when date and today option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.TODAY.value,
            selectedDate,
          },
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.dates]: { from, to: endOfDay } },
        ])
      })

      it('should fetch with date filter when date and currentWeek option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.CURRENT_WEEK.value,
            selectedDate,
          },
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.dates]: { from, to: endOfWeek } },
        ])
      })

      it('should fetch with date filter when date and currentWeekEnd option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.CURRENT_WEEK_END.value,
            selectedDate,
          },
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.dates]: { from: startNextWeekEnd, to: endOfWeek } },
        ])
      })

      it('should fetch with date filter when date and picked option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.USER_PICK.value,
            selectedDate,
          },
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.dates]: { from: startOfDay, to: endOfDay } },
        ])
      })
    })

    describe('by time only', () => {
      it('should fetch with time filter when timeRange is provided', () => {
        const timeRange = [18, 22]
        const filters = buildNumericFilters({ timeRange })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.times]: { from: 64800, to: 79200 } },
        ])
      })
    })

    describe('by date and time', () => {
      const timeRange = [18, 22]
      const from = '2021-05-05T18:00:00.000Z'
      const to = '2021-05-05T22:00:00.000Z'

      it('should fetch with date filter when timeRange, date and today option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.TODAY.value,
            selectedDate,
          },
          timeRange,
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.dates]: { from, to } },
        ])
      })

      it('should fetch with date filter when timeRange, date and currentWeek option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.CURRENT_WEEK.value,
            selectedDate,
          },
          timeRange,
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          ...[5, 6, 7, 8, 9].map(day => ({
            [AppSearchFields.dates]: {
              from: `2021-05-0${day}T18:00:00.000Z`,
              to: `2021-05-0${day}T22:00:00.000Z`,
            },
          })),
        ])
      })

      it('should fetch with date filter when timeRange, date and currentWeekEnd option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.CURRENT_WEEK_END.value,
            selectedDate,
          },
          timeRange,
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          ...[8, 9].map(day => ({
            [AppSearchFields.dates]: {
              from: `2021-05-0${day}T18:00:00.000Z`,
              to: `2021-05-0${day}T22:00:00.000Z`,
            },
          })),
        ])
      })

      it('should fetch with date filter when timeRange, date and picked option are provided', () => {
        const filters = buildNumericFilters({
          date: {
            option: DATE_FILTER.USER_PICK.value,
            selectedDate,
          },
          timeRange,
        })

        expect(filters).toStrictEqual([
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.dates]: { from, to } },
        ])
      })
    })
  })

  describe('beginningDatetime & endingDatetime', () => {
    const beginningDatetime = new Date(2020, 8, 1, 2, 3, 4)
    const endingDatetime = new Date(2020, 8, 2, 3, 4, 5)

    const from = '2020-09-01T02:05:00.000Z'
    const to = '2020-09-02T03:05:00.000Z'

    it('should fetch from the beginning datetime', () => {
      const filters = buildNumericFilters({ beginningDatetime })
      expect(filters).toStrictEqual([
        { [AppSearchFields.prices]: { to: 30000 } },
        { [AppSearchFields.dates]: { from } },
      ])
    })

    it('should fetch until the ending datetime', () => {
      const filters = buildNumericFilters({ endingDatetime })
      expect(filters).toStrictEqual([
        { [AppSearchFields.prices]: { to: 30000 } },
        { [AppSearchFields.dates]: { to } },
      ])
    })

    it('should fetch from the beginning datetime to the ending datetime', () => {
      const filters = buildNumericFilters({ beginningDatetime, endingDatetime })
      expect(filters).toStrictEqual([
        { [AppSearchFields.prices]: { to: 30000 } },
        { [AppSearchFields.dates]: { from, to } },
      ])
    })
  })
})
