import { createSelector } from 'reselect'

const array_chunks = (array, chunk_size) =>
  Array(Math.ceil(array.length / chunk_size))
    .fill()
    .map((_, index) => index * chunk_size)
    .map(begin => array.slice(begin, begin + chunk_size))

export default createSelector(
  state => state.user && state.user.offerers,
  (state, ownProps) => ownProps.columnsCount || 2,
  (offerers, columnsCount) =>
    offerers && array_chunks(offerers, columnsCount)
)
