// INITIAL STATE
const initialState = {
  category: null
}

// ACTIONS
const SET_FORM_CATEGORY = 'SET_FORM_CATEGORY'

// REDUCER
const form = (state = initialState, action) => {
  switch (action.type) {
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

// default
export default form
