export const reinitializeState = (state, initialState, config) => {
  if (!config.excludes) return initialState

  return Object.keys(initialState).reduce((resetState, currentStateKey) => {
    if (!config.excludes.includes(currentStateKey)) {
      resetState[currentStateKey] = initialState[currentStateKey]
    } else {
      resetState[currentStateKey] = state[currentStateKey]
    }

    return resetState
  }, {})
}
