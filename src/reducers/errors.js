// ACTIONS
const ASSIGN_ERRORS = 'ASSIGN_ERRORS'
const REMOVE_ERRORS = 'REMOVE_ERRORS'
const RESET_ERRORS = 'RESET_ERRRORS'

// INITIAL STATE
const initialState = {}

// REDUCER
const errors = (state = initialState, action) => {
  switch (action.type) {
    case ASSIGN_ERRORS:
      const nextState = {}
      action.errors.forEach(error => {
        Object.assign(nextState, error)
      })
      return Object.assign({}, state, nextState)
    case REMOVE_ERRORS:
      return Object.assign({}, state, {
          [action.name]: null,
        })
    case RESET_ERRORS:
      return initialState
    default:
      return state
  }
}

// ACTION CREATORS
export const assignErrors = errors => ({
  errors,
  type: ASSIGN_ERRORS,
})

export const removeErrors = name => ({
  name,
  type: REMOVE_ERRORS,
})

export const resetErrors = () => ({
  type: RESET_ERRORS
})


// default
export default errors
