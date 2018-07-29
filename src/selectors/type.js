import createCachedSelector from 're-reselect'

import typesSelector from './types'

export default createCachedSelector(
  state => typesSelector(state),
  (state, value) => value,
  (types, value) => types.find(t => t.value === value)
)((state, value) => value || '')
