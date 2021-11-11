import track from 'react-tracking'

import TrackEventWrapper from 'components/matomo/trackEventWrapper'

const withTracking = page => track({ page }, { dispatch: TrackEventWrapper })

export default withTracking
