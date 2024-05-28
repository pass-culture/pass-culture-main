import { configureStore } from '@reduxjs/toolkit'

import { rootReducer } from './rootReducer'

export const createStore = (initialState = {}) => {
  const store = configureStore({
    reducer: rootReducer,
    preloadedState: initialState,
    // Increase timeouts for checks that are only in dev mode
    // https://stackoverflow.com/a/69624806
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        immutableCheck: { warnAfter: 128 },
        serializableCheck: { warnAfter: 128 },
      }),
  })

  return { store }
}
