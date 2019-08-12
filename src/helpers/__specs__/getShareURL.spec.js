import { getShareURL } from '../getShareURL'

describe('src | helpers | getShareURL', () => {
  describe('when user is not defined', () => {
    it('should return null', () => {
      expect(getShareURL()).toBeNull()
    })
  })

  describe('when user is null', () => {
    it('should return null', () => {
      const user = null

      expect(getShareURL(user)).toBeNull()
    })
  })

  describe('when user is an empty object', () => {
    it('should return null', () => {
      const user = {}

      expect(getShareURL(user)).toBeNull()
    })
  })

  describe('when user has no id', () => {
    it('should return null', () => {
      const user = { prop: 'a string' }

      expect(getShareURL(user)).toBeNull()
    })
  })

  describe('when user id is not valid', () => {
    it('should return null', () => {
      const user = { id: [] }

      expect(getShareURL(user)).toBeNull()
    })
  })

  describe('when user id is an empty string', () => {
    it('should return null', () => {
      const user = { id: '' }

      expect(getShareURL(user)).toBeNull()
    })
  })

  describe('when user is valid', () => {
    describe('when offerId is defined', () => {
      describe('when mediationId is not defined', () => {
        it('should return null', () => {
          const user = { id: 'myId' }
          const offerId = 'AB'

          expect(getShareURL(user, offerId)).toBeNull()
        })
      })

      describe('when mediationId is defined', () => {
        it('should build url', () => {
          const user = { id: 'v9' }
          const offerId = 'AB'
          const mediationId = 'CD'

          const expected = 'http://localhost/decouverte/AB/CD?shared_by=v9'
          expect(getShareURL(user, offerId, mediationId)).toBe(expected)
        })
      })
    })
  })
})
