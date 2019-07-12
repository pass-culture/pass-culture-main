import { compose } from 'redux'

import Reimbursements from './Reimbursements'
import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'

export default compose(withRedirectToSigninWhenNotAuthenticated)(Reimbursements)
