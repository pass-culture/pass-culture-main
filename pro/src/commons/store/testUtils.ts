import { initialState as featuresInitialState } from '@/commons/store/features/reducer'
import { initialState as snackBarInitialState } from '@/commons/store/snackBar/reducer'
import { createStore, type RootState } from '@/commons/store/store'
import { initialState as userInitialState } from '@/commons/store/user/reducer'

export const configureTestStore = (overrideData?: Partial<RootState>) => {
  const initialData = {
    features: { ...featuresInitialState, initialized: true },
    snackBar: snackBarInitialState,
    user: userInitialState,
  }

  return createStore({ ...initialData, ...overrideData }).store
}
