import { getResolvedData } from '../utils/data'

// ACTION
const ASSIGN_DATA = 'ASSIGN_DATA'
const RESET_DATA = 'RESET_DATA'

// INITIAL STATE
const initialState = {}

// REDUCER
const data = (state = initialState, action) => {
  if (action.type === ASSIGN_DATA) {
    return Object.assign({}, state, action.patch)
  } else if (action.type === RESET_DATA) {
    return initialState
  } else if (/SUCCESS_DATA_(DELETE|GET|POST|PUT|PATCH)_(.*)/.test(action.type)) {
    // unpack config
    const key = action.config.key ||
      action.path.replace(/\/$/, '').replace(/\?.*$/, '')
    const nextState = {}

    // resolve
    nextState[key] = getResolvedData(
      // previousData
      state[key],
      // nextData: force to cast into array
      !Array.isArray(action.data)
        ? [action.data]
        : action.data,
      action.config
    )

    // last
    if (action.config.getSuccessState) {
      Object.assign(nextState, action.config.getSuccessState(state, action))
    }

    // return
    return Object.assign({}, state, nextState)

  }
  return state
}

// ACTION CREATORS
export const assignData = patch => ({
  patch,
  type: ASSIGN_DATA,
})

export const failData = (method, path, errors, config) => ({
  config,
  errors,
  method,
  path,
  type: `FAIL_DATA_${method.toUpperCase()}_${path.toUpperCase()}${
    config.local ? ' (LOCAL)' : ''
  }`,
})

export const requestData = (method, path, config = {}) => ({
  config,
  method,
  path,
  type: `REQUEST_DATA_${method.toUpperCase()}_${path.toUpperCase()}${
    config.local ? ' (LOCAL)' : ''
  }`,
})

export const resetData = () => ({
  type: RESET_DATA,
})

export const successData = (method, path, data, config = {}) => ({
  config,
  data,
  method,
  path,
  type: `SUCCESS_DATA_${method.toUpperCase()}_${path.toUpperCase()}${
    config.local ? ' (LOCAL)' : ''
  }`,
})

// default
export default data
