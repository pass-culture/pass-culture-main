import moment from 'moment'
import onCalendarUpdates from '../onCalendarUpdates'

const resetObj = { price: null, stockId: null, time: null }

describe('src | components | booking | utils | onCalendarUpdates', () => {
  it('should throw if no form values defined || not object', () => {
    expect(() => onCalendarUpdates()).toThrow('Missing arguments form values')
    expect(() => onCalendarUpdates(null)).toThrow('Missing arguments form values')
    expect(() => onCalendarUpdates(null, null)).toThrow('Missing arguments form values')
    let formValues = null
    expect(() => onCalendarUpdates(null, null, formValues)).toThrow('Missing arguments form values')
    formValues = undefined
    expect(() => onCalendarUpdates(null, null, formValues)).toThrow('Missing arguments form values')
    formValues = false
    expect(() => onCalendarUpdates(null, null, formValues)).toThrow('Missing arguments form values')
  })

  it('should not throw if form values is object', () => {
    const formValues = { price: null, stockId: null, time: null }
    expect(() => onCalendarUpdates(null, null, formValues)).not.toThrow()
  })

  it('should returns form values if selection is falsey', () => {
    const formValues = {}
    let selection = null
    let result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(formValues)
    selection = false
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(formValues)
    selection = undefined
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(formValues)
    selection = 0
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(formValues)
  })

  it('should returns default form values if no user selection', () => {
    const formValues = {}
    let selection = true
    let result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = []
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = () => {}
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = {}
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = 1234
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = { date: null }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = { date: 'a string' }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    selection = { date: [] }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
  })

  it('returns reset object if no bookables or not array or empty array', () => {
    const selection = { date: moment() }
    let formValues = {}
    let result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    formValues = { bookables: null }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    formValues = { bookables: undefined }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    formValues = { bookables: 0 }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    formValues = { bookables: {} }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
    formValues = { bookables: [] }
    result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
  })

  it('returns reset object if no matches between bookables and selection', () => {
    const mom2 = moment().add(2, 'days')
    const selection = { date: moment() }
    const formValues = {
      bookables: [{ beginningDatetime: null }, {}, { beginningDatetime: mom2 }],
    }
    const result = onCalendarUpdates(selection, null, formValues)
    expect(result).toStrictEqual(resetObj)
  })

  it('returns expected if matching', () => {
    const mom = moment()
    const match = { beginningDatetime: mom, id: 'AAA', price: 1 }
    const expected = { price: 1, stockId: 'AAA', time: 'AAA' }
    const formValues = {
      bookables: [match],
    }
    const result = onCalendarUpdates(mom, null, formValues)
    expect(result).toStrictEqual(expected)
  })

  it('returns first expected value if multiple matching', () => {
    const mom = moment()
    const match1 = { beginningDatetime: mom, id: 'AAA', price: 1 }
    const match2 = { beginningDatetime: mom, id: 'BBB', price: 1 }
    const expected = { price: 1, stockId: 'AAA', time: 'AAA' }
    const formValues = {
      bookables: [match1, match2],
    }
    const result = onCalendarUpdates(mom, null, formValues)
    expect(result).toStrictEqual(expected)
  })
})
