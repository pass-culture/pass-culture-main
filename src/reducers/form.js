// INITIAL STATE
const initialState = {}

// ACTIONS
const ASSIGN_FORM = 'ASSIGN_FORM'
const RESET_FORM = 'RESET_FORM'

// REDUCER
const form = (state = initialState, action) => {
  switch (action.type) {
    case ASSIGN_FORM:
      return Object.assign({}, state, action.patch)
    case RESET_FORM:
      return {}
    default:
      return state
  }
}

// ACTION CREATORS
export const assignForm = patch => ({
  patch,
  type: ASSIGN_FORM
})

export const resetForm = patch => ({ type: RESET_FORM })

// default
export default form
