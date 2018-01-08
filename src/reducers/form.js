// INITIAL STATE
const initialState = {
  category: null
}

// ACTIONS
const ASSIGN_FORM = 'ASSIGN_FORM'
const SET_FORM_CATEGORY = 'SET_FORM_CATEGORY'

// REDUCER
const form = (state = initialState, action) => {
  switch (action.type) {
    case ASSIGN_FORM:
      return Object.assign({}, state, action.patch)
    case SET_FORM_CATEGORY:
      return Object.assign({}, state, { category: action.category })
    default:
      return state
  }
}

// ACTION CREATORS
export const setFormCategory = category => ({
  category,
  type: SET_FORM_CATEGORY
})

export const assignForm = patch => ({
  patch,
  type: ASSIGN_FORM
})

// default
export default form
