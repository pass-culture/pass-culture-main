import { createSelector } from 'reselect'

import { SUCCESS } from '../reducers/queries'

export default createSelector(
  state => state.queries,
  queries => queries.find(q => q.key === 'occasions' &&
    q.status === SUCCESS)
)
