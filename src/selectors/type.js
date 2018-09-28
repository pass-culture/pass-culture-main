import createCachedSelector from 're-reselect'

import typesSelector from './types'

export default createCachedSelector(
  typesSelector,
  (state, isVirtual, value) => value,
  (types, value) => types.find(t => t.value === value)
)((state, isVirtual, value) => `${isVirtual || ''}${value || ''}`)
