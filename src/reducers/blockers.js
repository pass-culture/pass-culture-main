export const ADD_BLOCKERS = 'ADD_BLOCKERS'
export const REMOVE_BLOCKERS = 'REMOVE_BLOCKERS'

export default (state = [], action) => {
  switch (action.type) {
    case ADD_BLOCKERS:
      return state.concat([{ block: action.block, name: action.name }])
    case REMOVE_BLOCKERS:
      return state.filter(blocker => blocker.name !== action.name)
    default:
      return state
  }
}

// ACTION CREATORS
export const addBlockers = (name, block) => ({
  block,
  name,
  type: ADD_BLOCKERS,
})

export const removeBlockers = name => ({
  name,
  type: REMOVE_BLOCKERS,
})
