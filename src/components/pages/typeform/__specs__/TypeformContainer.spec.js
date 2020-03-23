import { getCurrentUserUUID } from '../../../hocs/with-login/with-login'

import { mapDispatchToProps, mapStateToProps } from '../TypeformContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
  }
})

describe('src | components |pages | typeform | TypeformContainer', () => {
  describe('mapStateToProps', () => {
    it('should return empty object when current user is not defined', () => {
      // given
      const state = { data: { users: [] } }

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({
        needsToFillCulturalSurvey: undefined,
      })
    })

    it('should return an url with search parameters: currentUser.id', () => {
      // given
      const state = {
        data: {
          users: [
            {
              currentUserUUID: getCurrentUserUUID(),
              needsToFillCulturalSurvey: true,
            },
          ],
        },
      }

      // when
      const result = mapStateToProps(state)

      // then
      const expected = {
        needsToFillCulturalSurvey: true,
      }
      expect(result).toStrictEqual(expected)
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch
    let functions

    beforeEach(() => {
      dispatch = jest.fn()
      functions = mapDispatchToProps(dispatch)
    })

    describe('flagUserHasFilledTypeform', () => {
      it('should dispatch an action with the right parameters', () => {
        // given
        const { flagUserHasFilledTypeform } = functions
        jest.spyOn(global.Date, 'now').mockImplementation(() => 1575201600)

        // when
        flagUserHasFilledTypeform(1)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/users/current',
            body: {
              culturalSurveyId: 1,
              culturalSurveyFilledDate: '1970-01-19T05:33:21Z',
              needsToFillCulturalSurvey: false,
            },
            isMergingDatum: true,
            method: 'PATCH',
          },
          type: 'REQUEST_DATA_PATCH_/USERS/CURRENT',
        })
      })
    })
  })
})
