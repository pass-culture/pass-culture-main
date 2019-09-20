import track from 'react-tracking'
import { trackEventWrapper } from '../../helpers/matomo/trackEventWrapper'

const withTracking = page => track({ page }, { dispatch: trackEventWrapper })

export default withTracking
