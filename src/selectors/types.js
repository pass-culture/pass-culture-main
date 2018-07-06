import createCachedSelector from 're-reselect';

export default createCachedSelector(
  state => state.data.types,
  types => types.map(t => {
      const [model, tag] = t.value.split('.')
      return Object.assign({ model, tag }, t)
    })
    // FOR NOW REMOVE THE BOOK TYPES
    .filter(t => t.model === 'EventType'),
  state => true
)
