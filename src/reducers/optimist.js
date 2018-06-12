// REDUCER
const optimist = (state = initialState, action) => {
  if (/REQUEST_DATA_(POST|PUT|DELETE|PATCH)_(.*)/.test(action.type)) {
    const nextState = {
      isOptimist: true,
      previousOptimistState: state
    }
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
    // unpack config
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

    // resolve
    nextState[key] = getResolvedData(action.method, action.path ,previousData, nextData, action.config)

    // get optimist keep
    if (action.method === 'GET' && state.isOptimist) {
      nextState.previousOptimistState = nextState
    }

    // clear the optimist when it is the POST PUT success
    if (
      action.method === 'POST' ||
      action.method === 'PUT' ||
      action.method === 'PATCH'
    ) {
      nextState.previousOptimistState = null
    }
    // special deprecation
    if (
      action.method === 'GET' &&
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
