import { combineReducers, createStore } from 'redux'
import { failData, successData, _requestData } from '../../data/actionCreators'
import { deleteRequests } from '../actionCreators'
import createRequestsReducer from '../createRequestsReducer'

const mockNowDate = 1487076708000
Date.now = jest.spyOn(Date, 'now').mockImplementation(() => mockNowDate)

describe('src | createRequestsReducer', () => {
  describe('when REQUEST_DATA', () => {
    it('should assign a pending request object', () => {
      // given
      const rootReducer = combineReducers({ requests: createRequestsReducer() })
      const store = createStore(rootReducer)

      // when
      store.dispatch(_requestData({ apiPath: '/foos' }))

      // then
      expect(store.getState().requests['/foos']).toStrictEqual({
        date: new Date(mockNowDate).toISOString(),
        errors: null,
        isPending: true,
        isError: false,
        isSuccess: false,
      })
    })
  })
  describe('when SUCCESS_DATA', () => {
    it('should assign a success request object', () => {
      // given
      const rootReducer = combineReducers({ requests: createRequestsReducer() })
      const store = createStore(rootReducer)

      // when
      store.dispatch(
        successData({ data: [{ foo: 'AE' }] }, { apiPath: '/foos' })
      )

      // then
      expect(store.getState().requests['/foos']).toStrictEqual({
        date: new Date(mockNowDate).toISOString(),
        errors: null,
        headers: undefined,
        isPending: false,
        isError: false,
        isSuccess: true,
      })
    })
  })
  describe('when FAIL_DATA', () => {
    it('should assign a fail request object', () => {
      // given
      const rootReducer = combineReducers({ requests: createRequestsReducer() })
      const store = createStore(rootReducer)

      // when
      store.dispatch(
        failData(
          { errors: [{ foo: 'missing something' }] },
          { apiPath: '/foos' }
        )
      )

      // then
      expect(store.getState().requests['/foos']).toStrictEqual({
        date: new Date(mockNowDate).toISOString(),
        errors: { foo: 'missing something' },
        headers: undefined,
        isPending: false,
        isError: true,
        isSuccess: false,
      })
    })
  })
  describe('when DELETE_REQUEST', () => {
    it('should delete a specific request object', () => {
      // given
      const rootReducer = combineReducers({
        requests: createRequestsReducer({
          '/foos': {
            date: new Date(mockNowDate).toISOString(),
            errors: null,
            headers: undefined,
            isPending: false,
            isError: false,
            isSuccess: true,
          },
        }),
      })
      const store = createStore(rootReducer)

      // when
      store.dispatch(deleteRequests('/foos'))

      // then
      expect(store.getState().requests['/foos']).toBeUndefined()
    })
  })
})
