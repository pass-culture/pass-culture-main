import { compose } from 'redux'
import withRequiredLogin from '../../../hocs/with-login/withRequiredLogin'

import PersonalInformations from './PersonalInformations'

export default compose(withRequiredLogin)(PersonalInformations)
