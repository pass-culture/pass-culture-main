/* eslint no-console: 0, max-nested-callbacks: 0 */
import MyHelper from './my/helper/relative/path'

describe('MyHelper', function() {
  beforeEach(function() {})
  afterEach(function() {})
  it('it expect something', function() {
    const value = { prop: 'prop' }
    const expected = { prop: 'prop' }
    const result = MyHelper(value)
    expect(expected).toStrictEqual(result)
  })
})
