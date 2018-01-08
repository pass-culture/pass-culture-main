// INITIAL STATE
const initialState = {
  offers: null,
  token: 'bd2b9fa5-fbee-434f-9aaf-adc6701fd3db',
  works: null
}

// REDUCER
const request = (state = initialState, action) => {
  if (/SUCCESS_(.*)/.test(action.type)) {
    return Object.assign({}, state, { [action.path.split('/').slice(-1)[0]]: action.data })
  }
  return state
}

// ACTION CREATORS
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

// default
export default request
