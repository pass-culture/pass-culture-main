/* eslint no-console: 0, max-nested-callbacks: 0 */
// TEST COMMAND
// ./node_modules/.bin/jest --env=jsdom ./path/to/file.spec.js --watch
import { parseOnlineOfferURL } from '../parseOnlineOfferURL'

describe('src | helpers | parseOnlineOfferURL', () => {
  it("n'est pas une string, retourne la valeur en argument", () => {
    let value = ''
    let expected = ''
    let result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = false
    expected = false
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = []
    expected = []
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = undefined
    expected = undefined
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    expect(result).toStrictEqual(expected)
    value = { prop: 'prop ' }
    expected = { prop: 'prop ' }
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
  })
  it("retourne l'url si elle contient http(s)", () => {
    let value = 'http://google.com'
    let expected = 'http://google.com'
    let result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = 'https://google.com'
    expected = 'https://google.com'
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = 'http://www.google.com'
    expected = 'http://www.google.com'
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = 'https://www.google.com'
    expected = 'https://www.google.com'
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
  })
  it("retourne l'url préfixée si ne contient pas http(s)", () => {
    let value = '//google.com'
    let expected = 'https://google.com'
    let result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = 'www.google.com'
    expected = 'https://www.google.com'
    result = parseOnlineOfferURL(value)
    expect(result).toStrictEqual(expected)
    value = 'undefined'
    expected = 'https://undefined'
    result = parseOnlineOfferURL(value)
    value = 'www.google.com/lorem-ipsum'
    expected = 'https://www.google.com/lorem-ipsum'
    result = parseOnlineOfferURL(value)
    value = 'google.com/lorem-ipsum'
    expected = 'https://www.google.com/lorem-ipsum'
    result = parseOnlineOfferURL(value)
  })
  it("retourne l'url préfixée si ne contient pas http", () => {
    const value = '//google.com'
    const expected = 'http://google.com'
    const result = parseOnlineOfferURL(value, 'http://')
    expect(result).toStrictEqual(expected)
  })
})
