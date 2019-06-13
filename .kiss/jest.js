// $(yarn bin)/jest --env=jsdom ./src/components/tests/component.spec.js --watch
import MyHelper from './src/components/component'
describe('src | components | component', function() {
  beforeEach(function() {})
  afterEach(function() {})
  it('it expect something', function() {
    const value = { prop: 'prop' }
    const expected = { prop: 'prop' }
    const result = MyHelper(value)
    expect(result).toStrictEqual(expected)
  })
})
