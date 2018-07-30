import { createData } from 'pass-culture-shared'

// ACTIONS
export const ASSIGN_DATA = 'ASSIGN_DATA'
export const FILTER_DATA = 'FILTER_DATA'
export const REMOVE_DATA_ERROR = 'REMOVE_DATA_ERROR'
export const RESET_DATA = 'RESET_DATA'

// INITIAL STATE
const initialState = { bookings: [], referenceDate: null, isOptimist: false }
const data = createData(initialState)

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

export const filterData = (key, filter) => ({
  filter,
  key,
  type: FILTER_DATA,
})

export const removeDataError = name => ({
  name,
  type: REMOVE_DATA_ERROR,
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
