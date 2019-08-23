import { createSelector } from 'reselect'

const selectData = state => state.data || {}
const selectOfferers = createSelector(
  selectData,
  data => data.offerers || []
)

export default selectOfferers
