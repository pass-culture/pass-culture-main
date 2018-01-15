// ACTIONS
export const CLOSE_MODAL = 'CLOSE_MODAL'
export const SHOW_MODAL = 'SHOW_MODAL'

// INITIAL STATE
const initialState = {
  content: null,
  isActive: false
}

// REDUCER
function modal (state = initialState, action) {
  switch (action.type) {
    case CLOSE_MODAL:
      return Object.assign({}, state, {
        isActive: false
      })
    case SHOW_MODAL:
      return Object.assign({}, state, {
        isActive: true,
        ContentComponent: action.ContentComponent || state.ContentComponent
      })
    default:
      return state
  }
}

// ACTION CREATORS
export function closeModal () {
  return { type: CLOSE_MODAL }
}

export function showModal (newContent) {
  return {
    ContentComponent: () => newContent,
    type: SHOW_MODAL
  }
}

// default
export default modal
