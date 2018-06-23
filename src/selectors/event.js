import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.events,
  (state, ownProps) => get(ownProps, 'occasion.eventId'),
  (events, eventId) => events && events.find(event =>
    event.id === eventId)
)
