import { getShareURL } from '../getShareURL'

describe('src | helpers | getShareURL', () => {
  it('to return false', () => {
    const expected = false
    let result = getShareURL()
    expect(expected).toStrictEqual(result)
    let location = null
    result = getShareURL(location)
    expect(expected).toStrictEqual(result)
    let user = null
    result = getShareURL(location, user)
    expect(expected).toStrictEqual(result)
    user = []
    location = []
    result = getShareURL(location, user)
    expect(expected).toStrictEqual(result)
    user = {}
    location = {}
    result = getShareURL(location, user)
    expect(expected).toStrictEqual(result)
    user = { prop: 'a string' }
    location = { search: '' }
    result = getShareURL(location, user)
    expect(expected).toStrictEqual(result)
    user = { id: [] }
    location = { search: 'a string' }
    result = getShareURL(location, user)
    expect(expected).toStrictEqual(result)
    user = { id: '' }
    location = { search: 'a string' }
    result = getShareURL(location, user)
    expect(expected).toStrictEqual(result)
  })

  it('an URL with shared_by argument', () => {
    let url = 'http://localhost'
    let expected = 'http://localhost?shared_by=v9'
    let user = { id: 'v9' }
    let location = { search: '' }
    let result = getShareURL(location, user, url)
    expect(expected).toStrictEqual(result)
    url = 'http://localhost?prop=value'
    expected = 'http://localhost?prop=value&shared_by=v9'
    user = { id: 'v9' }
    location = { search: '?prop=value' }
    result = getShareURL(location, user, url)
    expect(expected).toStrictEqual(result)
    url = 'http://localhost?prop=value'
    expected = 'http://localhost?prop=value&shared_by=v9'
    user = { id: 'v9' }
    location = { search: '' }
    result = getShareURL(location, user, url)
    expect(expected).toStrictEqual(result)
    url = 'http://localhost?prop=value&prop2=value2'
    expected = 'http://localhost?prop=value&prop2=value2&shared_by=v9'
    user = { id: 'v9' }
    location = { search: '' }
    result = getShareURL(location, user, url)
    expect(expected).toStrictEqual(result)
    url = 'http://localhost?prop=value&prop2=value2'
    expected = 'http://localhost?prop=value&prop2=value2&shared_by=v9'
    user = { id: 'v9' }
    location = { search: 'prop=value&prop2=value2' }
    result = getShareURL(location, user, url)
    expect(expected).toStrictEqual(result)
  })
})
