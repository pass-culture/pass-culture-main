import { compose } from 'redux'

import Reimbursements from './Reimbursements'
import { withRequiredLogin } from 'components/hocs'

export default compose(withRequiredLogin)(Reimbursements)
