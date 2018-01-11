// INITIAL STATE
const initialState = { isOptimist: false }

// REDUCER
const request = (state = initialState, action) => {
  if (/REQUEST_(POST|PUT|DELETE)_(.*)/.test(action.type)) {
    if (action.config && action.config.getOptimistState) {
      const newState = { isOptimist: true }
      const optimistState = action.config.getOptimistState(state, action)
      Object.assign(newState, optimistState)
      return Object.assign({}, state, newState)
    }
    return state
  } else if (/SUCCESS_GET_(.*)/.test(action.type)) {
    const key = action.config.key || action.path.split('/')[0].replace(/\?.*$/, '')
    const newState = { isOptimist: false }
    if (action.config.add === 'append') {
      newState[key] = state[key].concat(action.data)
    } else if (action.config.add === 'prepend') {
      newState[key] = action.data.concat(state[key])
    } else {
      newState[key] = action.data
    }
    return Object.assign({}, state, newState)
  }
  return state
}

// ACTION CREATORS
export const failData = (method, path, error, config) => ({
  config,
  error,
  method,
  path,
  type: `FAIL_${method.toUpperCase()}_${path.toUpperCase()}`
})

export const requestData = (method, path, config) => ({
  config,
  method,
  path,
  type: `REQUEST_${method.toUpperCase()}_${path.toUpperCase()}`
})

export const successData = (method, path, data, config={}) => ({
  config,
  data,
  method,
  path,
  type: `SUCCESS_${method.toUpperCase()}_${path.toUpperCase()}`
})

// SELECTORS
export const getCurrentWork = ({ request: { works } }) =>
  works && works.length === 1 && works[0]

export const getToken = (state, type) => {
  return state.request[`${type}Token`]
}

// default
export default request
