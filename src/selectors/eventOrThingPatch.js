import get from 'lodash.get'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  (state, event) => event,
  (state, event, thing) => thing,
  (state, event, thing, offerer) => offerer,
  (state, event, thing, venue) => venue,
  (event, thing, offerer, venue) =>
    Object.assign(
      {
        offererId: get(offerer, 'id'),
        venueId: get(venue, 'id'),
      },
      event || thing
    )
)(
  (state, event, thing, offerer, venue) =>
    `${get(event, 'id', ' ')}/${get(thing, 'id', ' ')}/${get(
      offerer,
      'id',
      ' '
    )}/${get(venue, 'id', ' ')}`
)
