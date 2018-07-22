import get from 'lodash.get'

const initialState = {}

const MERGE_FORM_DATA = 'MERGE_FORM_DATA'
const MERGE_FORM_ERROR = 'MERGE_FORM_ERROR'
const REMOVE_FORM_ERROR = 'REMOVE_FORM_ERROR'
const RESET_FORM = 'RESET_FORM'

const form = (state = initialState, action) => {
  switch (action.type) {
    case MERGE_FORM_DATA:
      const nextData = Object.assign({}, get(state, `${action.name}.data`))
      for (let key of Object.keys(action.data)) {
        const nextValue = action.data[key]
        if (nextValue === '') {
          if (nextData[key]) {
            delete nextData[key]

          }
          continue
        }
        nextData[key] = nextValue
      }
      return Object.assign({}, state, {
        [action.name]: Object.assign({}, state[action.name], {
          data: nextData
        })
      })
    case MERGE_FORM_ERROR:
      return Object.assign({}, state, {
        [action.name]: Object.assign({}, state[action.name], {
          errors: [].concat(action.data)
        })
      })
    case REMOVE_FORM_ERROR:
      return Object.assign({}, state, {
        [action.name]: Object.assign({}, state[action.name], {
          errors: []
        })
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

export const removeFormError = (name) => ({
  type: REMOVE_FORM_ERROR,
  name,
})

export const resetForm = () => ({
  type: RESET_FORM
})

export default form
