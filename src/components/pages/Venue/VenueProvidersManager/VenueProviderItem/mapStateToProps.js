import selectEventsByProviderId from 'selectors/selectEventsByProviderId'
import selectThingsByProviderId from 'selectors/selectThingsByProviderId'

function mapStateToProps(state, ownProps) {
  const {
    venueProvider: { providerId },
  } = ownProps
  return {
    events: selectEventsByProviderId(state, providerId),
    things: selectThingsByProviderId(state, providerId),
  }
}

export default mapStateToProps
