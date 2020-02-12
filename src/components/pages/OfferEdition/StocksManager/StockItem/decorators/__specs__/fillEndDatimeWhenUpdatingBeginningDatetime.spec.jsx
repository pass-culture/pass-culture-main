import { updateEndDateTimeField } from '../fillEndDatimeWhenUpdatingBeginningDatetime'

const europeTimezone = 'Europe/Paris'
const americaTimezone = 'America/Cayenne'

describe('components | OfferEdition | fillEndDatimeWhenUpdatingBeginningDatetime', () => {
  let allValues
  let triggerDate
  let doublonTriggerDateName
  let prevValues
  let targetDateName
  let targetTimeName

  beforeEach(() => {
    triggerDate = '2020-02-02T19:00:59.000Z'
    doublonTriggerDateName = 'beginningDatetime'
    allValues = {
      bookingLimitDatetime: '2020-01-29T22:59:59.805Z',
      beginningDatetime: '2020-02-02T19:00:59.000Z',
      endDatetime: '2020-01-31T22:00:59.000Z',
      beginningTime: '20:00',
      endTime: '23:00',
    }
    prevValues = {
      bookingLimitDatetime: '2020-01-29T22:59:59.805Z',
      beginningDatetime: '2020-01-31T19:00:59.000Z',
      endDatetime: '2020-01-31T22:00:59.000Z',
      beginningTime: '20:00',
      endTime: '23:00',
    }
    targetDateName = 'endDatetime'
    targetTimeName = 'endTime'
  })

  describe('with time zone europe', () => {
    it('should update the endDateTime date to the beginningDateTime with keeping hours and minute of previous target date, when both dates are already initialized', () => {
      // given
      const timezone = europeTimezone

      // when
      const result = updateEndDateTimeField(
        triggerDate,
        doublonTriggerDateName,
        allValues,
        prevValues,
        targetDateName,
        targetTimeName,
        timezone
      )
      const expected = {
        endDatetime: '2020-02-02T21:00:59.000Z',
      }

      // then
      expect(result).toStrictEqual(expected)
    })
  })

  describe('with time zone americ', () => {
    it('should update the endDateTime date to the beginningDateTime with keeping hours and minute of previous target date, when both dates are already initialized', () => {
      // given
      const timezone = americaTimezone

      // when
      const result = updateEndDateTimeField(
        triggerDate,
        doublonTriggerDateName,
        allValues,
        prevValues,
        targetDateName,
        targetTimeName,
        timezone
      )
      const expected = {
        endDatetime: '2020-02-03T01:00:59.000Z',
      }

      // then
      expect(result).toStrictEqual(expected)
    })
  })
})
