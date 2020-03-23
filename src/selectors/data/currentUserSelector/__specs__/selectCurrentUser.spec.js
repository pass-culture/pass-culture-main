import selectCurrentUser from '../selectCurrentUser'
import currentUserUUID from '../currentUserUUID'

describe('selectCurrentUser', () => {
  describe('when there is no users in state', () => {
    it('should be undefined', () => {
      // given
      const state = {
        data: {
          users: [],
        },
      }

      // when
      const result = selectCurrentUser(state)

      // then
      expect(result).toBeUndefined()
    })
  })

  describe('when there is a current user in state', () => {
    it('should return current user informations', () => {
      // given
      const state = {
        data: {
          users: [
            {
              currentUserUUID: currentUserUUID,
              id: 'FY',
              activity: null,
              canBookFreeOffers: true,
              civility: null,
              dateCreated: '2020-03-23T13:00:42.887007Z',
              dateOfBirth: null,
              departementCode: '93',
              email: 'pctest.jeune93.has-booked-some@btmx.fr',
              expenses: {
                all: { actual: 0, max: 500 },
                physical: { actual: 0, max: 500 },
                digital: { actual: 0, max: 500 },
              },
              firstName: 'PC Test Jeune',
              hasOffers: false,
              hasPhysicalVenues: false,
              isAdmin: false,
              lastName: '93 HBS',
              modelName: 'User',
              needsToFillCulturalSurvey: false,
              phoneNumber: null,
              postalCode: '93100',
              publicName: 'PC Test Jeune 93 HBS',
              wallet_balance: 231,
              wallet_date_created: '2020-03-23T13:00:42.886788Z',
              wallet_is_activated: true,
            },
          ],
        },
      }

      // when
      const result = selectCurrentUser(state)

      // then
      expect(result).toStrictEqual({
        currentUserUUID: currentUserUUID,
        id: 'FY',
        activity: null,
        canBookFreeOffers: true,
        civility: null,
        dateCreated: '2020-03-23T13:00:42.887007Z',
        dateOfBirth: null,
        departementCode: '93',
        email: 'pctest.jeune93.has-booked-some@btmx.fr',
        expenses: {
          all: { actual: 0, max: 500 },
          physical: { actual: 0, max: 500 },
          digital: { actual: 0, max: 500 },
        },
        firstName: 'PC Test Jeune',
        hasOffers: false,
        hasPhysicalVenues: false,
        isAdmin: false,
        lastName: '93 HBS',
        modelName: 'User',
        needsToFillCulturalSurvey: false,
        phoneNumber: null,
        postalCode: '93100',
        publicName: 'PC Test Jeune 93 HBS',
        wallet_balance: 231,
        wallet_date_created: '2020-03-23T13:00:42.886788Z',
        wallet_is_activated: true,
      })
    })
  })
})
