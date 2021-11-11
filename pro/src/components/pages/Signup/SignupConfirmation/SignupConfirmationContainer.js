/*
* @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
*/

import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import SignupConfirmation from './SignupConfirmation'

export default compose(withRouter)(SignupConfirmation)
