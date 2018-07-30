import queries, { PENDING, SUCCESS } from '../queries'

describe('src | reducers | queries  ', () => {
  describe('queries', () => {
    let state
    beforeEach(() => {
      state = [
        {
          data: {},
        },
      ]
    })

    it('should return the initial state by default', () => {
      // given
      const action = {}

      // when
      const updatedState = queries(state, action)

      // then
      expect(updatedState).toEqual(state)
    })

    describe('When action.type is REQUEST_DATA', () => {
      it('should return correct update state', () => {
        // given
        const action = {
          type: 'REQUEST_DATA_PUT_RECOMMENDATIONS',
          id: 'fakeRequestId',
          method: 'PUT',
          path: 'recommendations',
          config: {
            key: 'fakeKey',
            requestId: 'fakeRequestId',
          },
        }

        // when
        const queriesReducer = queries(state, action)
        const expected = [
          state[0],
          {
            id: 'fakeRequestId',
            path: 'recommendations',
            status: PENDING,
          },
        ]
        // then
        expect(queriesReducer).toEqual(expected)
      })
    })

    describe('When action.type is SUCCESS_DATA and not PENDING', () => {
      const currentState = [
        {
          id: 'fakeRequestId',
          path: 'recommendations?',
          status: SUCCESS,
        },
      ]
      it('should return correct update state', () => {
        // given
        const action = {
          config: {
            key: 'users',
            local: false,
            requestId: 'fakeRequestId',
          },
          method: 'GET',
          path: 'users/current',
          type: 'SUCCESS_DATA_GET_USERS/CURRENT',
        }

        // when
        const queriesReducer = queries(currentState, action)
        const expected = [
          {
            id: 'fakeRequestId',
            status: SUCCESS,
          },
        ]
        // then
        expect(queriesReducer).toEqual(expected)
      })
    })

    describe('When action.type is SUCCESS_DATA and PENDING', () => {
      const currentState = [
        {
          id: 'fakeRequestId',
          path: 'recommendations?',
          status: PENDING,
        },
      ]
      it('should return correct update state', () => {
        // given
        const action = {
          config: {
            key: 'users',
            local: false,
            requestId: 'fakeRequestId',
          },
          method: 'GET',
          path: 'users/current',
          type: 'SUCCESS_DATA_GET_USERS/CURRENT',
        }

        // when
        const queriesReducer = queries(currentState, action)

        // then
        expect(queriesReducer).toEqual([])
      })
    })
  })
})
