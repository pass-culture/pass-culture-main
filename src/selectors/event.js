import get from 'lodash.get'
import { createSelector } from 'reselect'

const createSelectEvent = () => createSelector(
  state => state.data.events,
  (state, ownProps) => get(ownProps, 'occasion.eventId'),
  (events, eventId) => events && events.find(event =>
    event.id === eventId)
)
export default createSelectEvent

export const selectCurrentEvent = createSelectEvent()
