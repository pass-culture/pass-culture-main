import createCachedSelector from 're-reselect';

export default createCachedSelector(
  state => state.data.searchedOfferers || state.data.offerers,
  offerers => offerers,
  () => true
)
