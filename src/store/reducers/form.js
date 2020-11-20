import merge from 'lodash.merge'

const initialState = {}

export const RESET_FORM = 'RESET_FORM'

export const form = (state = initialState, action) => {
  if (/MERGE_FORM_(.*)/.test(action.type)) {
    const nextPatch = Object.assign({}, state[action.name])

    for (let key of Object.keys(action.patch || {})) {
      const nextValue = action.patch[key]

      // THE CASE WHERE THE USER DELETED ALL THE CARACTERS
      // IN THE INPUT FIELD
      // WE NEED HERE TO COMPLETELY DELETE THE CORRESPONDING ITEM
      // IN THE FORM
      if (nextValue === '' || Number.isNaN(nextValue)) {
        if (nextPatch[key]) {
          delete nextPatch[key]
        }
        continue
      }

      // IF THE VALUE IS A PLAIN OBJECT, WE MERGE IT WITH THE PREVIOUS
      // VALUE, ELSE WE JUST SET IT
      if (action.config && action.config.isMergingObject) {
        nextPatch[key] = merge({}, nextPatch[key], nextValue)
      } else {
        nextPatch[key] = nextValue
      }
    }

    return Object.assign({}, state, {
      [action.name]: nextPatch,
    })
  }

  if (action.type === RESET_FORM) {
    return initialState
  }

  return state
}

export const mergeForm = (name, patch, config) => {
  let type = `MERGE_FORM_${name.toUpperCase()}`

  const patchKeys = patch && Object.keys(patch)
  if (patchKeys && patchKeys.length === 1) {
    const singleKey = patchKeys[0]
    type = `${type}_${singleKey.toUpperCase()}`
  }

  return {
    config,
    name,
    patch,
    type,
  }
}

export const resetForm = () => ({
  type: RESET_FORM,
})
