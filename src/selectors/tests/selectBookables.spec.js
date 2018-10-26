// yarn test:unit ./src/selectors/tests/selectBookables.spec.js  --watch
import moment from 'moment'
import { addModifierString, humanizeBeginningDate } from '../selectBookables'

describe('src | selectors| selectBookables', () => {
  describe('addModifierString', () => {
    it("ajoute une propriété nommée __modifiers__ aux objects d'un array", () => {
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
    it('transforme une date timezone en date lisible par un user, ajoute une propriété', () => {
      const dateString = '2018-11-02T19:30:24Z'
      const dateMoment = moment('2018-11-02T19:30:24Z')
      const dateFomated = 'Friday 02/11/2018 à 20:30'
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
          humanBeginningDate: dateFomated,
          prop: 'prop',
        },
        {
          beginningDatetime: dateString,
          humanBeginningDate: dateFomated,
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
  // describe('mapStockToBookable', () => {})
  // describe('markAsReserved', () => {})
  // describe('sortByDate', () => {})
  // describe('selectBookables', () => {})
})
