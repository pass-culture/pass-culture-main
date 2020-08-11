import { applyMiddleware, combineReducers, createStore } from 'redux'
import thunk from 'redux-thunk'
import { createDataReducer } from 'redux-thunk-data'

export function configureTestStore() {
  const storeEnhancer = applyMiddleware(thunk.withExtraArgument({ rootUrl: 'http://foo.com' }))
  const rootReducer = combineReducers({
    data: createDataReducer({ features: [], users: [] }),
  })

  return createStore(rootReducer, storeEnhancer)
}
