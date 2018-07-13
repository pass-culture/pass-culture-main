import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state) => state.data.types,
  (state, typeId) => typeId,
  // eslint-disable-next-line eqeqeq
  (types, typeId) => types.find(t => t.id == typeId) // id can be a string
)(
  (state, typeId) => (typeId || '')
)
