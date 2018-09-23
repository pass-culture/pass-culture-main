/* eslint no-console: 0, max-nested-callbacks: 0 */
// TEST COMMAND
// ./node_modules/.bin/jest --env=jsdom ./src/helpers/getShareURL.spec.js --watch
import { getShareURL } from './getShareURL'

describe('src | helpers | getShareURL', () => {
  it('to return false', () => {
    const expected = false
    let result = getShareURL()
    expect(expected).toEqual(result)
    let location = null
    result = getShareURL(location)
    expect(expected).toEqual(result)
    let user = null
    result = getShareURL(location, user)
    expect(expected).toEqual(result)
    user = []
    location = []
    result = getShareURL(location, user)
    expect(expected).toEqual(result)
    user = {}
    location = {}
    result = getShareURL(location, user)
    expect(expected).toEqual(result)
    user = { prop: 'a string' }
    location = { search: '' }
    result = getShareURL(location, user)
    expect(expected).toEqual(result)
    user = { id: [] }
    location = { search: 'a string' }
    result = getShareURL(location, user)
    expect(expected).toEqual(result)
    user = { id: '' }
    location = { search: 'a string' }
    result = getShareURL(location, user)
    expect(expected).toEqual(result)
  })

  it('an URL with shared_by argument', () => {
    let url = 'http://localhost'
    let expected = 'http://localhost?shared_by=v9'
    let user = { id: 'v9' }
    let location = { search: '' }
    let result = getShareURL(location, user, url)
    expect(expected).toEqual(result)
    url = 'http://localhost?prop=value'
    expected = 'http://localhost?prop=value&shared_by=v9'
    user = { id: 'v9' }
    location = { search: '?prop=value' }
    result = getShareURL(location, user, url)
    expect(expected).toEqual(result)
    url = 'http://localhost?prop=value'
    expected = 'http://localhost?prop=value&shared_by=v9'
    user = { id: 'v9' }
    location = { search: '' }
    result = getShareURL(location, user, url)
    expect(expected).toEqual(result)
    url = 'http://localhost?prop=value&prop2=value2'
    expected = 'http://localhost?prop=value&prop2=value2&shared_by=v9'
    user = { id: 'v9' }
    location = { search: '' }
    result = getShareURL(location, user, url)
    expect(expected).toEqual(result)
    url = 'http://localhost?prop=value&prop2=value2'
    expected = 'http://localhost?prop=value&prop2=value2&shared_by=v9'
    user = { id: 'v9' }
    location = { search: 'prop=value&prop2=value2' }
    result = getShareURL(location, user, url)
    expect(expected).toEqual(result)
  })
})
