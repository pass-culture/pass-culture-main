import { compose } from 'redux'

import Reimbursements from './Reimbursements'
import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'

export default compose(withRedirectToSigninWhenNotAuthenticated)(Reimbursements)
