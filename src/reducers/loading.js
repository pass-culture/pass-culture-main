export const SHOW_LOADING = 'SHOW_LOADING'
export const CLOSE_LOADING = 'CLOSE_LOADING'

const intialState = {
  isActive: false,
  tag: null,
}

function loading(state = intialState, action) {
  switch (action.type) {
    case SHOW_LOADING:
      return Object.assign({}, state, {
        isActive: true,
        tag: action.tag,
      })
    case CLOSE_LOADING:
      return Object.assign({}, state, {
        isActive: false,
        tag: null,
      })
    default:
      return state
  }
}

// ACTIONS
export function showLoading(tag) {
  return {
    tag,
    type: SHOW_LOADING,
  }
}

export function closeLoading() {
  return {
    type: CLOSE_LOADING,
  }
}

// default
export default loading
