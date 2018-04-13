// ACTIONS
const ASSIGN_DATA = 'ASSIGN_DATA'
const FILTER_DATA = 'FILTER_DATA'
const REMOVE_DATA_ERROR = 'REMOVE_DATA_ERROR'
const RESET_DATA = 'RESET_DATA'

// INITIAL STATE
const initialState = { referenceDate: null, isOptimist: false }

// REDUCER
const data = (state = initialState, action) => {
  if (action.type === ASSIGN_DATA) {
    return Object.assign({}, state, action.patch)
  } else if (action.type === FILTER_DATA) {
    const filteredElements = state[action.key].filter(action.filter)
    return Object.assign({}, state, { [action.key]: filteredElements })
  } else if (action.type === REMOVE_DATA_ERROR) {
    return Object.assign({}, state, {
      errors: Object.assign({}, state.errors, {
        [action.name]: null
      })
    })
  } else if (/REQUEST_DATA_(POST|PUT|DELETE|PATCH)_(.*)/.test(action.type)) {
    const nextState = { isOptimist: true, previousOptimistState: state }
    if (action.config && action.config.getOptimistState) {
      const nextState = { isOptimist: true, previousOptimistState: state }
      const optimistState = action.config.getOptimistState(state, action)
      Object.assign(nextState, optimistState)
      return Object.assign({}, state, nextState)
    }
    return Object.assign({}, state, nextState)
  } else if (action.type === RESET_DATA) {
    return initialState
  } else if (/SUCCESS_DATA_(GET|POST|PUT|PATCH)_(.*)/.test(action.type)) {
    const key = action.config.key ||
      action.path.replace(/\/$/, '').replace(/\?.*$/, '')
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
      // for put we need just to 'override pre existing data' or append it in the end
      nextState[key] = [...previousData]
      const previousIds = previousData.map(({ id }) => id)
      nextData.forEach(datum => {
        const previousIndex = previousIds.indexOf(datum.id)
        const putIndex = previousIndex === -1
          ? nextState[key].length
          : previousIndex
        nextState[key][putIndex] = Object.assign({},
          previousIndex !== -1 && nextState[key][previousIndex], datum)
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
      if (action.method === 'GET' && state.isOptimist) {
        nextState.previousOptimistState = nextState
      }
    }
    // clear the optimist when it is the POST PUT success
    if (action.method === 'POST' || action.method === 'PUT' || action.method === 'PATCH') {
      nextState.previousOptimistState = null
    }
    // special deprecation
    if (action.method === 'GET' &&
      action.config.local &&
      action.config.deprecatedData &&
      action.config.deprecatedData.length
    ) {
      const deprecatedKey = `deprecated${key[0].toUpperCase()}${key.slice(1)}`
      nextState[deprecatedKey] = action.config.deprecatedData
    }
    // last
    if (action.config.getSuccessState) {
      Object.assign(nextState, action.config.getSuccessState(state, action))
    }
    // return
    return Object.assign({}, previousState, nextState)
  } else if (/SUCCESS_DATA_DELETE_(.*)/.test(action.type)) {
    // init
    const nextState = { isOptimist: false }
    // update
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
  type: ASSIGN_DATA
})

export const failData = (method, path, errors, config) => ({
  config,
  errors,
  method,
  path,
  type: `FAIL_DATA_${method.toUpperCase()}_${path.toUpperCase()}${config.local ? ' (LOCAL)' : ''}`
})

export const filterData = (key, filter) => ({ filter,
  key,
  type: FILTER_DATA
})

export const removeDataError = name => ({
  name,
  type: REMOVE_DATA_ERROR
})

export const requestData = (method, path, config={}) => ({
  config,
  method,
  path,
  type: `REQUEST_DATA_${method.toUpperCase()}_${path.toUpperCase()}${config.local ? ' (LOCAL)' : ''}`
})

export const resetData = () => ({
  type: RESET_DATA
})

export const successData = (method, path, data, config={}) => ({
  config,
  data,
  method,
  path,
  type: `SUCCESS_DATA_${method.toUpperCase()}_${path.toUpperCase()}${config.local ? ' (LOCAL)' : ''}`
})

// default
export default data
