import { type AsyncThunkConfig, configureStore } from '@reduxjs/toolkit'

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

// We expose the store so that it can be used outside of the Redux context
export const { store: rootStore } = createStore()

// https://react-redux.js.org/using-react-redux/usage-with-typescript#define-root-state-and-dispatch-types
export type RootState = ReturnType<typeof rootStore.getState>
export type AppDispatch = typeof rootStore.dispatch
export type AppThunkApiConfig = AsyncThunkConfig & {
  dispatch: AppDispatch
  rejectValue: {
    body?: string
    error: string
    status?: number
  }
  state: RootState
}
