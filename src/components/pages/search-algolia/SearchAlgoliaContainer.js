import { compose } from 'redux'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import SearchAlgolia from './SearchAlgolia'

export default compose(withRequiredLogin)(SearchAlgolia)
