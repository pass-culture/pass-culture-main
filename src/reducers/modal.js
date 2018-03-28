// ACTIONS
export const CLOSE_MODAL = 'CLOSE_MODAL'
export const SHOW_MODAL = 'SHOW_MODAL'
export const LOCATION_CHANGE = '@@router/LOCATION_CHANGE'

// INITIAL STATE
const initialState = { ContentComponent: null,
  isActive: false
}

// REDUCER
function modal (state = initialState, action) {
  switch (action.type) {
    case CLOSE_MODAL:
      return Object.assign({}, state, {
        isActive: false
      })
    case LOCATION_CHANGE:
      return Object.assign({}, state, {
        isActive: false
      })
    case SHOW_MODAL:
      return Object.assign({}, state, {
        config: action.config || state.config,
        ContentComponent: action.ContentComponent || state.ContentComponent,
        isActive: true,
      })
    default:
      return state
  }
}

// ACTION CREATORS
export function closeModal() {
  return { type: CLOSE_MODAL }
}

export function showModal(modalElement, config) {
  return {
    config,
    ContentComponent: () => modalElement,
    type: SHOW_MODAL
  }
}

// default
export default modal
