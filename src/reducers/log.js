const LOG_LENGTH = 100;

// ACTIONS
export const APPEND_TO_LOG = 'APPEND_TO_LOG'

// INITIAL STATE
const initialState = []

// REDUCER
function logReduce(state = initialState, {type, method, ...values}) {
  switch (type) {
    case APPEND_TO_LOG:
      method = method || 'log'
      const time = new Date();
      console[method](`${method.toUpperCase()}:`, ...values)
      return state.slice(-LOG_LENGTH).concat({time, method, ...values})
    default:
      return state
  }
}

// ACTION CREATORS
export function debug(...values) {
  return {
    type: APPEND_TO_LOG,
    method: 'debug',
    ...values
  }
}
export function log(...values) {
  return {
    type: APPEND_TO_LOG,
    method: 'log',
    ...values
  }
}

export function warn(...values) {
  return {
    type: APPEND_TO_LOG,
    method: 'warn',
    ...values
  }
}
export function error(...values) {
  return {
    type: APPEND_TO_LOG,
    method: 'error',
    ...values
  }
}

// default
export default logReduce
