import { FeatureResponseModel } from 'apiClient/v1'

interface FeaturesState {
  initialized: boolean
  list: FeatureResponseModel[]
}

export const initialState: FeaturesState = {
  initialized: false,
  list: [],
}

// Features reducer has no action. The state is set when
// the store is configured in the <StoreProvider /> component
// The state never changes afterwards, we only use redux here
// as a global store with one selector and redux's built-in memoization
export const featuresReducer = (state = initialState) => {
  return state
}
