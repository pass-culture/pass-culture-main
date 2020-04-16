import { mapDispatchToProps } from '../TypeformContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')
  return {
    requestData,
  }
})

describe('src | components |pages | typeform | TypeformContainer', () => {
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
        const mockHandleSuccess = jest.fn()
        jest.spyOn(global.Date, 'now').mockImplementation(() => 1575201600)

        // when
        flagUserHasFilledTypeform(1, mockHandleSuccess)

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
            handleSuccess: mockHandleSuccess,
          },
          type: 'REQUEST_DATA_PATCH_/USERS/CURRENT',
        })
      })
    })
  })
})
