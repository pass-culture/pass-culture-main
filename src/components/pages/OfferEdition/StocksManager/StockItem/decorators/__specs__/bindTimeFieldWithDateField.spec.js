import 'moment-timezone'

import { updateDateFieldWithTime, updateTimeField } from '../bindTimeFieldWithDateField'

const europeTimezone = 'Europe/Paris'
const americaTimezone = 'America/Cayenne'

describe('src | components | pages | Offer | StockItem | decorators | bindTimeFieldWithDateField', () => {
  describe('updateDateFieldWithTime', () => {
    let allValues
    let doublonDateName
    let date
    let timeName
    let dateName

    beforeEach(() => {
      allValues = {
        bookingLimitDatetime: '2020-01-29T22:59:59.805Z',
        beginningDatetime: '2020-02-02T19:00:59.000Z',
        endDatetime: '2020-01-31T20:00:59.000Z',
        beginningTime: '18:00',
        endTime: '21:00',
      }
      doublonDateName = 'beginningDatetime'
      date = '2020-01-29T19:00:59.000Z'
      timeName = 'beginningTime'
      dateName = 'beginningDatetime'
    })

    describe('with time zone europe', () => {
      describe('when updating date field', () => {
        it('should return beginning date time with new beggining hour', () => {
          // given
          const timezone = europeTimezone

          // when
          const result = updateDateFieldWithTime(
            date,
            doublonDateName,
            allValues,
            timezone,
            timeName,
            dateName
          )
          const expected = {
            beginningDatetime: '2020-01-29T17:00:59.000Z',
          }

          // then
          expect(result).toStrictEqual(expected)
        })
      })
    })

    describe('with america timezone', () => {
      describe('when updating date field', () => {
        it('should return beginning date time with new beggining hour', () => {
          // given
          const timezone = americaTimezone

          // when
          const result = updateDateFieldWithTime(
            date,
            doublonDateName,
            allValues,
            timezone,
            timeName,
            dateName
          )
          const expected = {
            beginningDatetime: '2020-01-29T21:00:59.000Z',
          }

          // then
          expect(result).toStrictEqual(expected)
        })
      })
    })
  })

  describe('updateTimeField', () => {
    let allValues
    beforeEach(() => {
      allValues = {
        bookingLimitDatetime: '2020-01-29T19:00:59.805000Z',
        beginningDatetime: '2020-01-29T19:00:59.805000Z',
        endDatetime: '2020-01-29T22:00:59.805000Z',
        beginningTime: '18:00',
        endTime: '23:00',
      }
    })

    describe('when updating beginning time', () => {
      let time
      let doublonTimeName
      let timeName
      let dateName

      beforeEach(() => {
        time = '18:00'
        doublonTimeName = 'beginningTime'
        timeName = 'beginningTime'
        dateName = 'beginningDatetime'
      })

      describe('with time zone europe', () => {
        it('should update beginning date time with new hour', () => {
          // given
          const timezone = europeTimezone

          // when
          const result = updateTimeField(
            time,
            doublonTimeName,
            allValues,
            timezone,
            timeName,
            dateName
          )
          const expected = {
            beginningDatetime: '2020-01-29T17:00:59.805Z',
          }

          // then
          expect(result).toStrictEqual(expected)
        })
      })
      describe('with time zone america', () => {
        it('should update beginning date time with new hour', () => {
          // given
          const timezone = americaTimezone

          // when
          const result = updateTimeField(
            time,
            doublonTimeName,
            allValues,
            timezone,
            timeName,
            dateName
          )
          const expected = {
            beginningDatetime: '2020-01-29T21:00:59.805Z',
          }

          // then
          expect(result).toStrictEqual(expected)
        })
      })
    })
    describe('when updating end time ', () => {
      let time
      let doublonTimeName
      let timeName
      let dateName

      beforeEach(() => {
        doublonTimeName = 'endDatetime'
        timeName = 'endTime'
        dateName = 'endDatetime'
      })

      describe('with time zone europe', () => {
        it('should do update endDateTime with good ending hour', () => {
          // given
          const beginningShowTime = '18:00'
          const timezone = europeTimezone
          const time = beginningShowTime

          // when
          const result = updateTimeField(
            time,
            doublonTimeName,
            allValues,
            timezone,
            timeName,
            dateName
          )
          const expected = {
            endDatetime: '2020-01-29T17:00:59.805Z',
          }

          // then
          expect(result).toStrictEqual(expected)
        })
      })
      describe('with america timezone', () => {
        it('should do update endDateTime with good ending hour', () => {
          const timezone = americaTimezone
          const endingShowTime = '22:00'
          time = endingShowTime

          // when
          const result = updateTimeField(
            time,
            doublonTimeName,
            allValues,
            timezone,
            timeName,
            dateName
          )
          const expected = {
            endDatetime: '2020-01-30T01:00:59.805Z',
          }

          // then
          expect(result).toStrictEqual(expected)
        })
      })
    })
  })
})
