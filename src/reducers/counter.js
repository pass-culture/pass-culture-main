export const COUNTER_WAIT = 'COUNTER_WAIT'
export const COUNTER_TYPE = 'COUNTER_TYPE'
export const COUNTER_GET_VERIFICATION = 'COUNTER_GET_VERIFICATION'
export const COUNTER_RECEIVE_VERIFICATION = 'COUNTER_RECEIVE_VERIFICATION'
export const COUNTER_FAIL_VERIFICATION = 'COUNTER_FAIL_VERIFICATION'
export const COUNTER_POST_REGISTER = 'COUNTER_POST_REGISTER'
export const COUNTER_RECEIVE_REGISTER = 'COUNTER_RECEIVE_REGISTER'

const handledStateActions = [
  COUNTER_WAIT,
  COUNTER_TYPE,
  COUNTER_GET_VERIFICATION,
  COUNTER_FAIL_VERIFICATION,
  COUNTER_POST_REGISTER,
  COUNTER_RECEIVE_REGISTER,
]

const initialState = {
  counter: { state: 'COUNTER_WAITING', code: null, booking: null },
}

// -- REDUCERS -----------------------------------------------
const counter = (state = initialState, action) => {
  if (handledStateActions.indexOf(action.type) > -1) {
    return Object.assign({}, state, {
      state: action.type,
      code: action.payload,
    })
  }
  if (COUNTER_RECEIVE_VERIFICATION === action.type) {
    return Object.assign({}, state, {
      state: action.type,
      booking: action.payload,
    })
  }

  return state
}
export default counter

// -- ACTION CREATORS ----------------------------------------
export const wait = () => ({
  type: COUNTER_WAIT,
  payload: '',
})

export const type = code => ({
  type: COUNTER_TYPE,
  payload: code,
})

export const getVerification = code => ({
  type: COUNTER_GET_VERIFICATION,
  payload: code,
})

export const receiveVerification = (status, data) => ({
  type: COUNTER_RECEIVE_VERIFICATION,
  payload: {
    status,
    data,
  },
})

export const failVerification = () => ({
  type: COUNTER_FAIL_VERIFICATION,
})

export const postRegister = code => ({
  type: COUNTER_POST_REGISTER,
  payload: code,
})

export const codeReceiveRegister = status => ({
  type: COUNTER_RECEIVE_REGISTER,
  payload: status,
})
