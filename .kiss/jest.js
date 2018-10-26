/* eslint no-console: 0 */

// ./node_modules/.bin/jest --env=jsdom ./path/to/file.spec.js --watch
import MyHelper from './my/helper/relative/path'

describe('path | to | my | helper', function() {
  beforeEach(function() {})
  afterEach(function() {})
  it('it expect something', function() {
    const value = { prop: 'prop' }
    const expected = { prop: 'prop' }
    const result = MyHelper(value)
    expect(result).toStrictEqual(expected)
  })
})
