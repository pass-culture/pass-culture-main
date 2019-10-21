import { applyMiddleware, combineReducers, createStore } from 'redux'
import thunk from 'redux-thunk'

const getMockStore = reducers => {
  const enhancer = applyMiddleware(thunk.withExtraArgument({ rootUrl: 'http://fake-url.fr' }))
  const reducer = combineReducers(reducers)
  return createStore(reducer, enhancer)
}

export default getMockStore
