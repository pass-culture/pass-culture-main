import { compose } from 'redux'
import { withRouter } from 'react-router'
import withLogin from '../../hocs/with-login/withLogin'
import NotMatch from './NotMatch'

export default compose(
  withLogin({ isRequired: false }),
  withRouter
)(NotMatch)
