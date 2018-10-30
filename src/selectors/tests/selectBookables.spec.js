// yarn test:unit ./src/selectors/tests/selectBookables.spec.js  --watch
import moment from 'moment'
import { addModifierString, humanizeBeginningDate } from '../selectBookables'

const format = 'dddd DD/MM/YYYY à HH:mm'

describe('src | selectors| selectBookables', () => {
  describe('addModifierString', () => {
    it('Add property named __modifiers__ to array of objects', () => {
      let value = []
      let expected = []
      let result = addModifierString()(value)
      expect(result).toStrictEqual(expected)
      value = [{ prop: 'prop' }]
      expected = [{ __modifiers__: ['selectBookables'], prop: 'prop' }]
      result = addModifierString()(value)
      expect(result).toStrictEqual(expected)
    })
  })
  describe('humanizeBeginningDate', () => {
    it('transform a date to an human readable one', () => {
      const dateString = new Date().toISOString()
      const dateMoment = moment(dateString)
      const dateExpected = dateMoment.format(format)
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
      result = humanizeBeginningDate()(value)
      expect(result).toStrictEqual(expected)
    })
  })
  xdescribe('mapStockToBookable', () => {})
  xdescribe('markAsReserved', () => {})
  xdescribe('sortByDate', () => {})
  xdescribe('selectBookables', () => {})
})
