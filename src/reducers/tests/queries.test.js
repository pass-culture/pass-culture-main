import queries,
{
  PENDING,
  SUCCESS
} from '../queries'

describe('src | reducers | queries  ', () => {

  describe('queries', () => {
    let state
    beforeEach(() => {
      state = [{
        data : {}
      }]
    })

    describe('When action.type is REQUEST_DATA', () => {
      it('should return correct update state', () => {
        // given
        const action = {
          type: 'REQUEST_DATA_PUT_RECOMMENDATIONS',
          id: 'fakeRequestId',
          method: 'PUT',
          path: 'recommendations',
          config : {
            key: 'fakeKey',
            requestId: 'fakeRequestId'
          }
        }

        // when
        const queriesReducer = queries(state, action)
        const expected = [
          state[0],
          {
          id: 'fakeRequestId',
          path: 'recommendations',
          status: PENDING
        }
      ]
        // then
        expect(queriesReducer).toEqual(expected)
      })
    })

    describe('When action.type is SUCCESS_DATA', () => {
      it('should return correct update state', () => {
        // given
        const action = {
            config: {
            key: 'users',
            local: false,
            requestId: 'fakeRequestIdRTYRYT'
          },
          method: 'GET',
          path: 'users/current',
          type: 'SUCCESS_DATA_GET_USERS/CURRENT'
        }

        // when
        const queriesReducer = queries(state, action,)
        const expected = [
          {
            id: undefined,
            status: SUCCESS
          }
        ]
        // then
        expect(queriesReducer).toEqual(state)
      })
    })
  })
})
