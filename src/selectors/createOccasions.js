import { createSelector } from 'reselect'

export default searchSelector => createSelector(
  state => state.data.searchedOccasions || state.data.occasions,
  (_, offererId, venueId) => offererId,
  (_, offererId, venueId) => venueId,
  (occasions, offererId, venueId) => {

    if (offererId)
      occasions = occasions.filter(o => o.lastProviderId === offererId)

    // TODO: find the link between occasion and venue
    if (venueId)
      occasions = occasions.filter(o => o.venueId === venueId)

    return occasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
