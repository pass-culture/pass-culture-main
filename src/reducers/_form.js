import get from 'lodash.get'
// import set from 'lodash.set'
import { DELETE, NEW } from '../utils/config'

import { deepMerge } from '../utils/object'

const initialState = {}

const MERGE_FORM_DATA = 'MERGE_FORM_DATA'
const MERGE_FORM_ERROR = 'MERGE_FORM_ERROR'
const REMOVE_FORM_DATA = 'REMOVE_FORM_DATA'
const REMOVE_FORM_ERROR = 'REMOVE_FORM_ERROR'
const RESET_FORM = 'RESET_FORM'

const form = (state = initialState, action) => {
  const collectionKey = `${action.collectionName}ById`
  const collection = Object.assign({}, state[collectionKey])
  switch (action.type) {
    case MERGE_FORM_DATA:
      /*
      const nextData = Object.keys(action.data).reduce((result, k) => {
        return set(result, k, action.data[k])
      }, {})
      */

      const nextData = {}
      for (let key of Object.keys(action.data)) {
        const nextValue = action.data[key]
        if (nextValue === '') {
          continue
        }
        nextData[key] = nextValue
      }
      console.log('nextData', nextData)

      return Object.assign({}, state, {
        [action.name]: Object.assign({}, state[action.name], { data: nextData })
      })


    case MERGE_FORM_ERROR:
      return deepMerge(state, {
        [action.name]: {
          errors: [].concat(action.data),
        }
      })
    /*
    case REMOVE_FORM_DATA:
      const nextData = get(state, `${action.name}.data`)
      if (!dataData) {
        return state
      }
      delete dataData[action.key]
      return deepMerge(state, {
        [action.name]: {
          data: dataData
        }
      })
    */
    case REMOVE_FORM_ERROR:
      return deepMerge(state, {
        [action.name]: {
          errors: []
        }
      })
    case RESET_FORM:
      return initialState
    default:
      return state
  }
}

export const mergeFormData = (name, data, config) => ({
  type: MERGE_FORM_DATA,
  name,
  data,
  config
})

export const mergeFormError = (name, data) => ({
  type: MERGE_FORM_ERROR,
  name,
  data,
})

/*
export const removeFormData = (name, key) => ({
  type: REMOVE_FORM_ERROR,
  name,
  key
})
*/

export const removeFormError = (name) => ({
  type: REMOVE_FORM_ERROR,
  name,
})

export const resetForm = () => ({
  type: RESET_FORM
})

export default form
