export const ASSIGN_MODAL_CONFIG = 'ASSIGN_MODAL_CONFIG'
export const CLOSE_MODAL = 'CLOSE_MODAL'
export const SHOW_MODAL = 'SHOW_MODAL'

export const initialState = {
  $modal: null,
  config: { fromDirection: 'right' },
  isActive: false,
}

const modal = (state = initialState, action) => {
  switch (action.type) {
    case CLOSE_MODAL:
      return Object.assign({}, state, {
        $modal: action.keepComponentMounted ? state.$modal : null,
        isActive: false,
      })
    case ASSIGN_MODAL_CONFIG:
      return Object.assign({}, state, {
        config: Object.assign({}, state.config, action.config),
      })
    case SHOW_MODAL:
      return Object.assign({}, state, {
        $modal: action.$modal,
        config: action.config,
        isActive: true,
      })
    default:
      return state
  }
}

export function assignModalConfig(config) {
  return { config, type: ASSIGN_MODAL_CONFIG }
}

export function closeModal(keepComponentMounted) {
  return { keepComponentMounted, type: CLOSE_MODAL }
}

export function showModal($modal, config) {
  return {
    $modal,
    config,
    type: SHOW_MODAL,
  }
}

export default modal
