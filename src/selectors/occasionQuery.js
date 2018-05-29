import { createSelector } from 'reselect'

const pathTest = /occasions\/(events|things)\/(.*)/

export default createSelector(
  state => state.queries,
  queries =>
    queries.find(query => pathTest.test(query.path))
)
