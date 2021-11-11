import { applyMiddleware, combineReducers, createStore } from 'redux'
import thunk from 'redux-thunk'

import { createDataReducer } from '../../../../utils/fetch-normalize-data/reducers/data/createDataReducer'

export function configureTestStore() {
  const storeEnhancer = applyMiddleware(thunk.withExtraArgument({ rootUrl: 'http://foo.com' }))
  const rootReducer = combineReducers({
    data: createDataReducer({ features: [], users: [] }),
  })

  return createStore(rootReducer, storeEnhancer)
}
