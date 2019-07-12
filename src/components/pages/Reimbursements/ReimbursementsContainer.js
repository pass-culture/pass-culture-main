import { compose } from 'redux'

import Reimbursements from './Reimbursements'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'

export default compose(withRedirectToSigninWhenNotAuthenticated)(Reimbursements)
