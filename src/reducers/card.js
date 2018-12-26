// ACTIONS
export const CLOSE_DETAILS_VIEW = 'CLOSE_DETAILS_VIEW'
export const LOCATION_CHANGE = '@@router/LOCATION_CHANGE'
export const MAKE_DRAGGABLE = 'MAKE_DRAGGABLE'
export const MAKE_UNDRAGGABLE = 'MAKE_UNDRAGGABLE'
export const SHOW_UNFLIPPABLE_DETAILS_VIEW = 'SHOW_UNFLIPPABLE_DETAILS_VIEW'
export const SHOW_DETAILS_VIEW = 'SHOW_DETAILS_VIEW'

// INITIAL STATE
const initialState = {
  areDetailsVisible: false,
  draggable: true,
  isActive: false,
  unFlippable: false,
}

// REDUCER
function card(state = initialState, action) {
  switch (action.type) {
    case CLOSE_DETAILS_VIEW:
      return Object.assign({}, state, { areDetailsVisible: false, unFlippable: false })
    case SHOW_DETAILS_VIEW:
      return Object.assign({}, state, { areDetailsVisible: true })
    case MAKE_UNDRAGGABLE:
      return Object.assign({}, state, { draggable: false })
    case MAKE_DRAGGABLE:
      return Object.assign({}, state, { draggable: true })
    case SHOW_UNFLIPPABLE_DETAILS_VIEW:
      return Object.assign({}, state, { areDetailsVisible: true, unFlippable: true })
    default:
      return state
  }
}

// ACTION CREATORS
export function showCardDetails() {
  return { type: SHOW_DETAILS_VIEW }
}

export function flipUnflippable() {
  return { type: SHOW_UNFLIPPABLE_DETAILS_VIEW }
}

export function makeDraggable() {
  return { type: MAKE_DRAGGABLE }
}

export function makeUndraggable() {
  return { type: MAKE_UNDRAGGABLE }
}

export function closeCardDetails() {
  return { type: CLOSE_DETAILS_VIEW }
}

// default
export default card
