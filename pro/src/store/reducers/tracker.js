/*
* @debt deprecated "Gaël: deprecated usage of redux-saga-data"
*/

import { getStateKeyFromApiPath, getStateKeyFromUrl } from 'redux-saga-data'

const initialState = {}

export const tracker = (state = initialState, action) => {
  if (
    /SUCCESS_DATA_(DELETE|GET|POST|PUT|PATCH)_(.*)/.test(action.type) &&
    action.config.method.toUpperCase() === 'GET'
  ) {
    const stateKey =
      action.config.stateKey ||
      (action.config.apiPath && getStateKeyFromApiPath(action.config.apiPath)) ||
      (action.config.url && getStateKeyFromUrl(action.config.url))

    return Object.assign({}, state, {
      [stateKey]: new Date(),
    })
  }
  return state
}
