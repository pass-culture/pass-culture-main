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
      const nextState = { isOptimist: true, previousOptimistState: state }
      const optimistState = action.config.getOptimistState(state, action)
      Object.assign(nextState, optimistState)
      return Object.assign({}, state, nextState)
    }
    return state
  } else if (/SUCCESS_DATA_(GET|POST|PUT)_(.*)/.test(action.type)) {
    const key = action.config.key || action.path.replace(/\/$/, '').replace(/\?.*$/, '')
    const nextState = { isOptimist: false }
    // force to cast into array
    let nextData = action.data
    if (!Array.isArray(nextData)) {
      nextData = [nextData]
    }
    // choose the previousState
    const previousState = action.method === 'GET'
      ? state
      : state.previousOptimistState || {}
    let previousData = previousState[key] || []
    if (!Array.isArray(previousData)) {
      previousData = [previousData]
    }
    // update
    if (action.method === 'PUT') {
      // for put we need just to 'override pre existing data'
      nextState[key] = [...previousData]
      const previousIds = previousData.map(({ id }) => id)
      nextData.forEach(datum => {
        const previousIndex = previousIds.indexOf(datum.id)
        nextState[key][previousIndex] = Object.assign({}, nextState[key][previousIndex], datum)
      })
    } else {
      // for get and post we need to concat
      if (action.config.add === 'append') {
        nextState[key] = previousData.concat(nextData)
      } else if (action.config.add === 'prepend') {
        nextState[key] = nextData.concat(previousData)
      } else {
        nextState[key] = nextData
      }
      // keep it the previousOptimistState when
      // it is a GET method
      // because it means that this success happens
      // between a REQUEST and a SUCCESS POST PUT actions
      if (action.method === 'GET') {
        nextState.previousOptimistState = nextState
      }
    }
    // clear the optimist when it is the POST PUT success
    if (action.method === 'POST' || action.method === 'PUT') {
      nextState.previousOptimistState = null
    }
    // last
    if (action.config.getSuccessState) {
      Object.assign(nextState, action.config.getSuccessState(state, action))
    }
    // return
    return Object.assign({}, previousState, nextState)
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
