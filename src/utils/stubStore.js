import { applyMiddleware, combineReducers, createStore } from 'redux'
import createSagaMiddleware from 'redux-saga'

export const getStubStore = reducers => {
  const enhancer = applyMiddleware(createSagaMiddleware())
  const reducer = combineReducers(reducers)

  return createStore(reducer, enhancer)
}
