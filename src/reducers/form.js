// import merge from 'lodash.merge'

import { NEW } from '../utils/config'

// INITIAL STATE
const initialState = {}

// ACTIONS
const MERGE_FORM = 'MERGE_FORM'
const RESET_FORM = 'RESET_FORM'

// REDUCER
const form = (state = initialState, action) => {
  switch (action.type) {
    case MERGE_FORM:
      const collectionKey = `${action.collectionName}ById`
      const collection = Object.assign({}, state[collectionKey])
      const entity = Object.assign({}, collection[action.id])
      collection[action.id] = entity
      entity[action.name] = action.value
      return Object.assign({}, state, { [collectionKey]: collection })
    // return merge({}, state, action.patch)
    case RESET_FORM:
      return {}
    default:
      return state
  }
}

// ACTION CREATORS
export const mergeForm = (collectionName, id, name, value) => ({
  collectionName,
  id,
  name,
  type: MERGE_FORM,
  value,
})

export const resetForm = patch => ({ type: RESET_FORM })

// SELECTORS
export function getFormCollection(state, ownProps) {
  const form = state.form
  if (!form) {
    return
  }
  return form[`${ownProps.collectionName}ById`]
}

export function getFormEntity(state, ownProps) {
  const collection = getFormCollection(state, ownProps)
  if (!collection) {
    return
  }
  return collection[ownProps.entityId || NEW]
}

export function getFormValue(state, ownProps) {
  const entity = getFormEntity(state, ownProps)
  if (!entity) {
    return
  }
  return entity[ownProps.name]
}

// default
export default form
