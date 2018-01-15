// INITIAL STATE
const initialState = {}

// ACTIONS
const ASSIGN_FORM = 'ASSIGN_FORM'
const MERGE_FORM = 'MERGE_FORM'
const RESET_FORM = 'RESET_FORM'

// REDUCER
const form = (state = initialState, action) => {
  switch (action.type) {
    case ASSIGN_FORM:
      return Object.assign({}, state, action.patch)
    case MERGE_FORM:
      const collectionKey = `${action.collectionName}ById`
      const collection = Object.assign({}, state[collectionKey])
      const entity = Object.assign({}, collection[action.id])
      collection[action.id] = entity
      entity[action.name] = action.value
      return Object.assign({}, state, { [collectionKey]: collection })
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

export const mergeForm = (collectionName, id, name, value) => ({
  collectionName,
  id,
  name,
  type: MERGE_FORM,
  value
})

export const resetForm = patch => ({ type: RESET_FORM })

// default
export default form
