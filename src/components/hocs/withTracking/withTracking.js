import track from 'react-tracking'

import TrackEventWrapper from '../../matomo/trackEventWrapper'

const withTracking = page => {
  return track({ page }, { dispatch: TrackEventWrapper })
}

export default withTracking
