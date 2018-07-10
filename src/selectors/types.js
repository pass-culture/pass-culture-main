import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.types,
  types => types.map(t => {
      const [model, tag] = t.value.split('.')
      return Object.assign({ model, tag }, t)
    })
    // FOR NOW REMOVE THE BOOK TYPES
    .filter(t => t.model === 'EventType')
)
