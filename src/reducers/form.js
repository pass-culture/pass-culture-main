import get from 'lodash.get'
import { DELETE, NEW } from '../utils/config'

// INITIAL STATE
const initialState = {}

// ACTIONS
const MERGE_FORM = 'MERGE_FORM'
const REMOVE_FORM = 'REMOVE_FORM'
const RESET_FORM = 'RESET_FORM'

// REDUCER
const form = (state = initialState, action) => {
  let collectionKey, collection
  switch (action.type) {
    case REMOVE_FORM:
      collectionKey = `${action.collectionName}ById`
      collection = Object.assign({}, state[collectionKey])
      delete collection[action.id]
      return Object.assign({}, state, { [collectionKey]: collection })
    case MERGE_FORM:
      collectionKey = `${action.collectionName}ById`
      collection = Object.assign({}, state[collectionKey])
      const entity = Object.assign({}, collection[action.id])
      if (typeof action.nameOrObject === 'object' && !action.value) {
        collection[action.id] = action.nameOrObject
      } else if (action.nameOrObject === DELETE) {
        collection[action.id] = DELETE
      } else {
        collection[action.id] = entity
        if (action.nameOrObject.includes('.')) {
          const chunks = action.nameOrObject.split('.')
          const chainKey = chunks.slice(0, -1).join('.')
          const lastKey = chunks.slice(-1)[0]
          let value = get(entity, chainKey)
          if (!value && !chainKey.includes('.')) {
            entity[chainKey] = action.parentValue
          }
          value = entity[chainKey]
          if (value) {
            value[lastKey] = action.value
          }
        } else  {
          entity[action.nameOrObject] = action.value
        }
      }
      return Object.assign({}, state, { [collectionKey]: collection })
    case RESET_FORM:
      return {}
    default:
      return state
  }
}

// ACTION CREATORS
export const mergeForm = (collectionName, id, nameOrObject, value, parentValue) => ({
  collectionName,
  id,
  nameOrObject,
  type: MERGE_FORM,
  value,
  parentValue
})

export const removeForm = (collectionName, id) => ({
  collectionName,
  id,
  type: REMOVE_FORM,
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
  console.log('ownProps', ownProps)
  const entity = getFormEntity(state, ownProps)
  if (!entity) {
    return
  }
  return entity[ownProps.name]
}

// default
export default form
