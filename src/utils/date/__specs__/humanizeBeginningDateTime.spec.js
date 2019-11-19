import moment from 'moment'

import { addModifierString } from '../../addModifierString'
import { humanizeBeginningDateTime } from '../humanizeBeginningDateTime'

const DAY_DATE_TIME_FORMAT = 'dddd DD/MM/YYYY à HH:mm'

describe('humanizeBeginningDate', () => {
  it('transform a date to an human readable one', () => {
    // Given
    const dateString = new Date().toISOString()
    const dateMoment = moment(dateString)
    const dateExpected = dateMoment.format(DAY_DATE_TIME_FORMAT)
    let value = []
    let expected = []
    let result = addModifierString()(value)
    expect(result).toStrictEqual(expected)
    value = [
      { beginningDatetime: '', prop: 'prop' },
      { prop: 'prop' },
      { beginningDatetime: dateMoment, prop: 'prop' },
      { beginningDatetime: dateString, prop: 'prop' },
      { beginningDatetime: 'this is no date', prop: 'prop' },
      { beginningDatetime: 42, prop: 'prop' },
    ]
    expected = [
      { beginningDatetime: '', prop: 'prop' },
      { prop: 'prop' },
      {
        beginningDatetime: dateMoment,
        humanBeginningDate: dateExpected,
        prop: 'prop',
      },
      {
        beginningDatetime: dateString,
        humanBeginningDate: dateExpected,
        prop: 'prop',
      },
      {
        beginningDatetime: 'this is no date',
        prop: 'prop',
      },
      {
        beginningDatetime: 42,
        prop: 'prop',
      },
    ]

    // When
    result = humanizeBeginningDateTime()(value)

    // Then
    expect(result).toStrictEqual(expected)
  })
})
