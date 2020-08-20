import withLogin from '../../../../hocs/with-login/withLogin'
import PageNotFound from './PageNotFound'

export default withLogin({ isRequired: false })(PageNotFound)
