import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.types,
  types =>
    types.filter(t => t.type === 'Event').map(t => {
      const [, value] = t.value.split('.')
      return Object.assign({}, t, { value })
    })
)
