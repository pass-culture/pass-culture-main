import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.mediations,
  (state, params) => params,
  (mediations, {id, type}) => {
    return mediations.filter(m => m[`${type}Id`] === id )
  }
)
