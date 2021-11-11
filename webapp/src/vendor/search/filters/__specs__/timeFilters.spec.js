import { TIME } from '../timeFilters'

const start = 1
const prevSaturday = new Date(2021, 4, start, 9, 30)
const prevSunday = new Date(2021, 4, start + 1, 9, 30)
const monday = new Date(2021, 4, start + 2, 9, 30)
const tuesday = new Date(2021, 4, start + 3, 9, 30)
const wednesday = new Date(2021, 4, start + 4, 9, 30)
const thursday = new Date(2021, 4, start + 5, 9, 30)
const friday = new Date(2021, 4, start + 6, 9, 30)
const saturday = new Date(2021, 4, start + 7, 9, 30)
const sunday = new Date(2021, 4, start + 8, 9, 30)

describe('time utilities', () => {
  describe('utils', () => {
    it('should getStartOfDay', () => {
      expect(TIME.getStartOfDay(new Date(2021, 4, 3, 9, 30))).toStrictEqual(new Date(2021, 4, 3))
    })

    it('should getEndOfDay', () => {
      expect(TIME.getEndOfDay(new Date(2021, 4, 3, 9, 30))).toStrictEqual(
        new Date(2021, 4, 3, 23, 59, 59)
      )
    })

    it('should getDateAtGivenHour', () => {
      expect(TIME.getDateAtGivenHour(new Date(2021, 4, 3, 9, 30), 22)).toStrictEqual(
        new Date(2021, 4, 3, 22)
      )
    })
  })

  describe('getStartOfWeekEnd', () => {
    it.each`
      currentDate     | expected
      ${prevSaturday} | ${prevSaturday}
      ${prevSunday}   | ${prevSunday}
      ${monday}       | ${saturday}
      ${tuesday}      | ${saturday}
      ${friday}       | ${saturday}
      ${saturday}     | ${saturday}
      ${sunday}       | ${sunday}
    `('startOfWeekEnd of $currentDate should be "$expected"', ({ currentDate, expected }) => {
      expect(TIME.getStartOfWeekEnd(currentDate)).toStrictEqual(TIME.getStartOfDay(expected))
    })
  })

  describe('getEndOfWeek', () => {
    it.each`
      currentDate     | expected
      ${prevSaturday} | ${prevSunday}
      ${prevSunday}   | ${prevSunday}
      ${monday}       | ${sunday}
      ${tuesday}      | ${sunday}
      ${friday}       | ${sunday}
      ${saturday}     | ${sunday}
      ${sunday}       | ${sunday}
    `('endOfWeek of $currentDate should be "$expected"', ({ currentDate, expected }) => {
      expect(TIME.getEndOfWeek(currentDate)).toStrictEqual(TIME.getEndOfDay(expected))
    })
  })

  describe('getWeekEndDatesFromDate', () => {
    it.each`
      currentDate     | expected
      ${prevSaturday} | ${[prevSaturday, prevSunday]}
      ${prevSunday}   | ${[prevSunday]}
      ${monday}       | ${[saturday, sunday]}
      ${tuesday}      | ${[saturday, sunday]}
      ${friday}       | ${[saturday, sunday]}
      ${saturday}     | ${[saturday, sunday]}
      ${sunday}       | ${[sunday]}
    `('should get week end dates of $currentDate', ({ currentDate, expected }) => {
      const weekEndDates = TIME.WEEK_END.getWeekEndDatesFromDate(currentDate)
      expect(weekEndDates).toHaveLength(expected.length)

      weekEndDates.forEach((date, index) => {
        expect(date).toStrictEqual(expected[index])
      })
    })
  })

  describe('getWeekDatesFromDate', () => {
    it.each`
      currentDate  | expected
      ${monday}    | ${[monday, tuesday, wednesday, thursday, friday, saturday, sunday]}
      ${tuesday}   | ${[tuesday, wednesday, thursday, friday, saturday, sunday]}
      ${wednesday} | ${[wednesday, thursday, friday, saturday, sunday]}
      ${thursday}  | ${[thursday, friday, saturday, sunday]}
      ${friday}    | ${[friday, saturday, sunday]}
      ${saturday}  | ${[saturday, sunday]}
      ${sunday}    | ${[sunday]}
    `('should get week dates of $currentDate', ({ currentDate, expected }) => {
      const weekDates = TIME.WEEK.getWeekDatesFromDate(currentDate)
      expect(weekDates).toHaveLength(expected.length)

      weekDates.forEach((date, index) => {
        expect(date).toStrictEqual(expected[index])
      })
    })
  })

  describe('getAllFromTimeRangeAndDate', () => {
    const timeRange = [20, 23]

    it('should get the time range for a selected day', () => {
      const times = TIME.getAllFromTimeRangeAndDate(wednesday, timeRange)
      expect(times).toStrictEqual([
        TIME.getDateAtGivenHour(wednesday, 20),
        TIME.getDateAtGivenHour(wednesday, 23),
      ])
    })

    it('should get the time range for a selected week end', () => {
      const times = TIME.WEEK_END.getAllFromTimeRangeAndDate(wednesday, timeRange)
      expect(times).toStrictEqual([
        [TIME.getDateAtGivenHour(saturday, 20), TIME.getDateAtGivenHour(saturday, 23)],
        [TIME.getDateAtGivenHour(sunday, 20), TIME.getDateAtGivenHour(sunday, 23)],
      ])
    })

    it('should get the time range for a selected week', () => {
      const times = TIME.WEEK.getAllFromTimeRangeAndDate(wednesday, timeRange)
      expect(times).toStrictEqual([
        ...[wednesday, thursday, friday, saturday, sunday].map(day => [
          TIME.getDateAtGivenHour(day, 20),
          TIME.getDateAtGivenHour(day, 23),
        ]),
      ])
    })
  })
})
