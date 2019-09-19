import { selectUserOffererByOffererIdAndUserIdAndRightsType } from '../userOfferersSelectors'

describe('src | selectors | data | userOfferersSelectors', () => {
  describe('selectUserOffererByOffererIdAndUserIdAndRightsType', () => {
    describe('when offererId, userId and rights string are given', () => {
      it('should find the first occurence matching the predicate', () => {
        const state = {
          data: {
            userOfferers: [
              {
                offererId: 'AE',
                userId: 'myUser',
                rights: 'admin',
              },
            ],
          },
        }
        const offererId = 'AE'
        const userId = 'myUser'
        const rights = 'admin'
        expect(
          selectUserOffererByOffererIdAndUserIdAndRightsType(state, offererId, userId, rights)
        ).toStrictEqual({ offererId: 'AE', userId: 'myUser', rights: 'admin' })
      })
    })

    describe('when offererId doesnt match', () => {
      it('should return undefined', () => {
        const state = {
          data: {
            userOfferers: [
              {
                offererId: 'AE',
                userId: 'myUser',
                rights: 'rights',
              },
            ],
          },
        }
        const offererId = 'NO'
        const userId = 'myUser'
        const rights = 'admin'
        expect(
          selectUserOffererByOffererIdAndUserIdAndRightsType(state, offererId, userId, rights)
        ).toBeUndefined()
      })
    })

    describe('when userId doesnt match', () => {
      it('should return undefined', () => {
        const state = {
          data: {
            userOfferers: [
              {
                offererId: 'AE',
                userId: 'myUser',
                rights: 'rights',
              },
            ],
          },
        }
        const offererId = 'AE'
        const userId = 'notMyUser'
        const rights = 'admin'
        expect(
          selectUserOffererByOffererIdAndUserIdAndRightsType(state, offererId, userId, rights)
        ).toBeUndefined()
      })
    })

    describe('when rights doesnt match', () => {
      it('should return undefined', () => {
        const state = {
          data: {
            userOfferers: [
              {
                offererId: 'AE',
                userId: 'myUser',
                rights: 'rights',
              },
            ],
          },
        }
        const offererId = 'AE'
        const userId = 'myUser'
        const rights = 'user'
        expect(
          selectUserOffererByOffererIdAndUserIdAndRightsType(state, offererId, userId, rights)
        ).toBeUndefined()
      })
    })
  })
})
