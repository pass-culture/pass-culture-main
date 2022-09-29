import { configureStore } from '@reduxjs/toolkit'

import rootReducer from './reducers'

const createStore = (initialState = {}) => {
  const store = configureStore({
    reducer: rootReducer,
    preloadedState: initialState,
  })

  return { store }
}

export default createStore
