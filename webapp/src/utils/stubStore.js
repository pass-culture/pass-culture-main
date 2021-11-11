import { applyMiddleware, combineReducers, createStore } from 'redux'
import thunk from 'redux-thunk'

export const getStubStore = reducers => {
  const enhancer = applyMiddleware(thunk.withExtraArgument({ rootUrl: 'http://fake-url.fr' }))
  const reducer = combineReducers(reducers)

  return createStore(reducer, enhancer)
}
