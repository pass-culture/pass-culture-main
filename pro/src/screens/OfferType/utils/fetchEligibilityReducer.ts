type EligibilityState = {
  hasBeenCalled: boolean;
  isEligible: boolean | null;
  isLoading: boolean;
}

export const initialState: EligibilityState = {
  hasBeenCalled: false,
  isEligible: null,
  isLoading: false,
}

export const FETCH_ACTION = { type: 'fetch' }
export const SUCCESS_ACTION = { type: 'success' }
export const FAILURE_ACTION = { type: 'failure' }

type EligibilityAction = typeof FETCH_ACTION | typeof SUCCESS_ACTION | typeof FAILURE_ACTION
  
export const reducer = (
  state: EligibilityState,
  action:EligibilityAction
): EligibilityState => {
  switch(action.type) {
    case 'fetch':
      return { ...state, hasBeenCalled: true, isLoading: true }
    case 'success':
      return { ...state, isLoading: false, isEligible: true }
    case 'failure':
      return { ...state, isLoading: false, isEligible: false }
    default:
      return state
  }
}
