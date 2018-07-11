import get from 'lodash.get'
import set from 'lodash.set'
import { DELETE, NEW } from '../utils/config'

import {deepMerge} from '../utils/object'

// INITIAL STATE
const initialState = {}

// ACTIONS
const MERGE_FORM = 'MERGE_FORM'
const NEW_MERGE_FORM = 'NEW_MERGE_FORM'
const REMOVE_FORM = 'REMOVE_FORM'
const RESET_FORM = 'RESET_FORM'
const NEW_ERROR_FORM = 'NEW_ERROR_FORM'

// REDUCER
const form = (state = initialState, action) => {
  const collectionKey = `${action.collectionName}ById`
  const collection = Object.assign({}, state[collectionKey])
  switch (action.type) {
    case NEW_MERGE_FORM:
      const newValue = Object.keys(action.values).reduce((result, k) => {
        return set(result, k, action.values[k])
      }, {})
      return deepMerge(state, {
        [action.name]: {
          data: newValue
        }
      })
    case NEW_ERROR_FORM:
      console.log(action)
      return deepMerge(state, {
        [action.name]: {
          errors: [].concat(action.values),
        }
      })
    case REMOVE_FORM:
      delete collection[action.id]
      return Object.assign({}, state, { [collectionKey]: collection })
    case MERGE_FORM:
      const entity = Object.assign({}, collection[action.id])
      if (typeof action.nameOrObject === 'object' && !action.value) {
        collection[action.id] = Object.assign({}, collection[action.id], action.nameOrObject)
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
export const newMergeForm = (name, values, options) => ({
  type: NEW_MERGE_FORM,
  name,
  values,
  options,
})

export const newErrorForm = (name, values) => ({
  type: NEW_ERROR_FORM,
  name,
  values,
})

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
  const entity = getFormEntity(state, ownProps)
  if (!entity) {
    return
  }
  return entity[ownProps.name]
}

// default
export default form
