import { getShareURL } from '../getShareURL'

describe('src | helpers | getShareURL', () => {
  describe('when url is not defined', () => {
    describe('when location, user are not defined', () => {
      it('should return false', () => {
        expect(getShareURL()).toStrictEqual(false)
      })
    })

    describe('when location is null and user is not defined', () => {
      it('should return false', () => {
        const location = null
        expect(getShareURL(location)).toStrictEqual(false)
      })
    })

    describe('when location and user are null', () => {
      it('should return false', () => {
        const location = null
        const user = null
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user and location are empty arrays', () => {
      it('should return false', () => {
        const user = []
        const location = []
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user and location are empty objects', () => {
      it('should return false', () => {
        const user = {}
        const location = {}
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user has no id, location is valid', () => {
      it('should return false', () => {
        const user = { prop: 'a string' }
        const location = { search: '' }
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user id is not valid, location is valid', () => {
      it('should return false', () => {
        const user = { id: [] }
        const location = { search: 'a string' }
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user id is an empty string, location is valid', () => {
      it('should return false', () => {
        const user = { id: '' }
        const location = { search: 'a string' }
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user is valid, location has no search', () => {
      it('should return false', () => {
        const user = { id: 'myId' }
        const location = { notSearch: 'not a search string' }
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })

    describe('when user is valid, location search is not a string', () => {
      it('should return false', () => {
        const user = { id: 'myId' }
        const location = { search: ['not a search string'] }
        expect(getShareURL(location, user)).toStrictEqual(false)
      })
    })
  })

  describe('when url is defined', () => {
    describe('when user id is defined and location search param is empty', () => {
      it('should append shared_by=user.id to url', () => {
        const url = 'http://localhost'
        const user = { id: 'v9' }
        const location = { search: '' }
        const result = getShareURL(location, user, url)
        expect(result).toStrictEqual('http://localhost?shared_by=v9')
      })
    })

    describe('when user id is defined and location search param equals url query param', () => {
      it('should not duplicate same search params', () => {
        const url = 'http://localhost?prop=value'
        const user = { id: 'v9' }
        const location = { search: '?prop=value' }
        const result = getShareURL(location, user, url)
        expect(result).toStrictEqual('http://localhost?prop=value&shared_by=v9')
      })
    })

    describe('when user id is defined and url already has one query param', () => {
      it('should keep url query param', () => {
        const url = 'http://localhost?prop=value'
        const user = { id: 'v9' }
        const location = { search: '' }
        const result = getShareURL(location, user, url)
        expect(result).toStrictEqual('http://localhost?prop=value&shared_by=v9')
      })
    })
  })
})
