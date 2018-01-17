// ACTIONS
const ASSIGN_DATA = 'ASSIGN_DATA'

// INITIAL STATE
const initialState = { isOptimist: false }

// REDUCER
const data = (state = initialState, action) => {
  if (action.type === ASSIGN_DATA) {
    return Object.assign({}, state, action.patch)
  } else if (/REQUEST_DATA_(POST|PUT|DELETE)_(.*)/.test(action.type)) {
    if (action.config && action.config.getOptimistState) {
      const newState = { isOptimist: true, previousOptimistState: state }
      const optimistState = action.config.getOptimistState(state, action)
      Object.assign(newState, optimistState)
      return Object.assign({}, state, newState)
    }
    return state
  } else if (/SUCCESS_DATA_(GET|POST|PUT)_(.*)/.test(action.type)) {
    const key = action.config.key || action.path.replace(/\/$/, '').replace(/\?.*$/, '')
    const newState = { isOptimist: false }
    // force to cast into array
    let data
    if (!Array.isArray(data)) {
      data = [data]
    }
    // choose the previousState
    const previousState = action.method === 'GET'
      ? state
      : state.previousOptimistState || {}
    let previousData = previousState[key]
    if (!Array.isArray(previousData)) {
      previousData = [previousData]
    }
    // update
    if (action.method === 'PUT') {
      // for put we need just to 'override pre existing data'
      newState[key] = [...previousData]
      const previousIds = previousData.map(({ id }) => id)
      action.data.forEach(datum => {
        const previousIndex = previousIds.indexOf(datum.id)
        newState[key][previousIndex] = Object.assign({}, newState[key][previousIndex], datum)
      })
    } else {
      // for get and post we need to concat
      if (action.config.add === 'append') {
        newState[key] = previousData.concat(action.data)
      } else if (action.config.add === 'prepend') {
        newState[key] = action.data.concat(previousData)
      } else {
        newState[key] = action.data
      }
    }
    // return
    return Object.assign({}, previousState, newState)
  }
  return state
}

// ACTION CREATORS
export const assignData = patch => ({
  patch,
  type: ASSIGN_DATA
})

export const failData = (method, path, error, config) => ({
  config,
  error,
  method,
  path,
  type: `FAIL_DATA_${method.toUpperCase()}_${path.toUpperCase()}`
})

export const requestData = (method, path, config) => ({
  config,
  method,
  path,
  type: `REQUEST_DATA_${method.toUpperCase()}_${path.toUpperCase()}`
})

export const successData = (method, path, data, config={}) => ({
  config,
  data,
  method,
  path,
  type: `SUCCESS_DATA_${method.toUpperCase()}_${path.toUpperCase()}`
})

// default
export default data
