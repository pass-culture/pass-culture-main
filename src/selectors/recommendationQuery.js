import { createSelector } from 'reselect'

export default createSelector(
  state => state.queries,
  queries => queries.find(query => /recommendations\/(.*)/.test(query.path))
)
