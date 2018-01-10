// INITIAL STATE
const initialState = {
  clientToken: 'bd2b9fa5-fbee-434f-9aaf-adc6701fd3db',
  offers: null,
  professionalToken: 'bd2b9fa5-fbee-434f-9aaf-adc6701fd3db',
  works: null
}

// REDUCER
const request = (state = initialState, action) => {
  if (/SUCCESS_(.*)/.test(action.type)) {
    return Object.assign({}, state, { [action.path.split('/')[0]]: action.data })
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

export const successData = (method, path, data, config) => ({
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
