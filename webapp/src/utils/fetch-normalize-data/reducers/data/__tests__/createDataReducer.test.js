import { combineReducers, createStore } from 'redux'
import {
  assignData,
  commitData,
  deleteData,
  reinitializeData,
  successData,
} from '../actionCreators'
import { createDataReducer } from '../createDataReducer'

Date.now = jest.spyOn(Date, 'now').mockImplementation(() => 1487076708000)

describe('src | createDataReducer', () => {
  describe('when ASSIGN_DATA', () => {
    it('should assign data', () => {
      // given
      const rootReducer = combineReducers({ data: createDataReducer({}) })
      const store = createStore(rootReducer)
      const foos = [{ id: 'AE' }]

      // when
      store.dispatch(assignData({ foos }))

      // then
      expect(store.getState().data.foos).toStrictEqual(foos)
    })
  })

  describe('when COMMIT_DATA', () => {
    it('should commit data', () => {
      // given
      const initialState = {
        commits: [],
        foos: [],
      }
      const rootReducer = combineReducers({
        data: createDataReducer(initialState),
      })
      const store = createStore(rootReducer)

      const firstDateCreated = new Date().toISOString()
      let secondDateCreated = new Date(firstDateCreated)
      secondDateCreated.setDate(secondDateCreated.getDate() + 1)
      secondDateCreated = secondDateCreated.toISOString()
      const commits = [
        {
          collectionName: 'foos',
          dateCreated: firstDateCreated,
          patch: {
            bar: 'ouech',
          },
          uuid: 1,
        },
        {
          collectionName: 'foos',
          dateCreated: firstDateCreated,
          patch: {
            mom: 'dad',
          },
          uuid: 2,
        },
        {
          collectionName: 'foos',
          dateCreated: secondDateCreated,
          patch: {
            pek: 1,
          },
          uuid: 1,
        },
      ]
      // when
      store.dispatch(commitData(commits))

      // then
      expect(store.getState().data).toStrictEqual({
        commits: [
          { ...commits[0], localIdentifier: `1/${commits[0].dateCreated}` },
          { ...commits[1], localIdentifier: `2/${commits[1].dateCreated}` },
          { ...commits[2], localIdentifier: `1/${commits[2].dateCreated}` },
        ],
        foos: [
          {
            bar: 'ouech',
            firstDateCreated: commits[0].dateCreated,
            lastDateCreated: commits[2].dateCreated,
            pek: 1,
            uuid: 1,
          },
          {
            firstDateCreated: commits[1].dateCreated,
            lastDateCreated: commits[1].dateCreated,
            mom: 'dad',
            uuid: 2,
          },
        ],
      })
    })
  })

  describe('when DELETE_DATA', () => {
    it('should delete data', () => {
      // given
      const bars = [
        {
          id: 'AE',
          __ACTIVITIES__: ['TO_BE_DELETED'],
        },
        {
          id: 'BF',
          __ACTIVITIES__: ['/bars'],
        },
      ]
      const foos = [
        {
          id: 'AE',
          __ACTIVITIES__: ['TO_BE_DELETED'],
        },
        {
          id: 'BF',
          __ACTIVITIES__: ['TO_BE_DELETED'],
        },
      ]
      const rootReducer = combineReducers({
        data: createDataReducer({
          bars,
          foos,
        }),
      })
      const store = createStore(rootReducer)

      // when
      store.dispatch(deleteData(null, { activityTags: ['TO_BE_DELETED'] }))

      // then
      const state = store.getState().data
      expect(state).toStrictEqual({
        bars: [
          {
            id: 'BF',
            __ACTIVITIES__: ['/bars'],
          },
        ],
        foos: [],
      })
    })
  })

  describe('when REINITIALIZE_DATA', () => {
    it('should reset data with no excludes', () => {
      // given
      const initialState = {
        bars: [{ id: 'FF' }],
        foos: [{ id: 'AE' }],
        totos: [{ id: 'DD' }],
      }
      const rootReducer = combineReducers({
        data: createDataReducer(initialState),
      })
      const store = createStore(rootReducer)

      // when
      store.dispatch(reinitializeData())

      // then
      expect(store.getState().data).toStrictEqual(initialState)
    })

    it('should reset data with excludes', () => {
      // given
      const initialState = {
        bars: [],
        foos: [{ id: 'AE' }],
        totos: [{ id: 'DD1' }],
      }
      const rootReducer = combineReducers({
        data: createDataReducer(initialState),
      })
      const store = createStore(rootReducer)
      store.dispatch(
        assignData({
          bars: [{ id: 'FF' }],
          foos: [],
          totos: [{ id: 'DD1' }, { id: 'DD2' }],
        })
      )

      // when
      store.dispatch(reinitializeData({ excludes: ['bars', 'totos'] }))

      // then
      expect(store.getState().data).toStrictEqual({
        bars: [{ id: 'FF' }],
        foos: [{ id: 'AE' }],
        totos: [{ id: 'DD1' }, { id: 'DD2' }],
      })
    })
  })

  describe('when SUCCESS_DATA', () => {
    it('should merge a patch inside the state with apiPath', () => {
      // given
      const initialState = { bars: [] }
      const rootReducer = combineReducers({
        data: createDataReducer(initialState),
      })
      const store = createStore(rootReducer)
      const foos = [{ id: 'AE' }]

      // when
      store.dispatch(successData({ data: foos, status: 200 }, { apiPath: '/foos', method: 'GET' }))

      // then
      const expectedFoos = foos.map(foo => ({
        ...foo,
        __ACTIVITIES__: ['/foos'],
      }))
      expect(store.getState().data).toStrictEqual({
        bars: [],
        foos: expectedFoos,
      })
    })

    it('should not merge a patch when stateKey is null', () => {
      // given
      const initialState = { bars: [] }
      const rootReducer = combineReducers({
        data: createDataReducer(initialState),
      })
      const store = createStore(rootReducer)
      const foos = [{ id: 'AE' }]

      // when
      store.dispatch(
        successData(
          { data: foos, status: 200 },
          { apiPath: '/foos', method: 'GET', stateKey: null }
        )
      )

      // then
      expect(store.getState().data).toStrictEqual({ bars: [] })
    })
  })
})
