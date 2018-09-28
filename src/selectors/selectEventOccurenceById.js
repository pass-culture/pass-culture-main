import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.eventOccurrences,
  (state, eventOccurenceId) => eventOccurenceId,
  (eventOccurrences, eventOccurenceId) =>
    eventOccurrences.find(
      eventOccurrence => eventOccurrence.id === eventOccurenceId
    )
)((state, eventOccurenceId) => eventOccurenceId || '')
