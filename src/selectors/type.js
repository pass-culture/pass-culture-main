import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state) => state.data.types,
  (state, typeId) => typeId,
  (types, typeId) => types.find(t => t.id.toString() === typeId.toString())
)(
  (state, typeId) => (typeId || '')
)
