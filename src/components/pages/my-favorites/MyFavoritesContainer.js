import { compose } from 'redux'

import MyFavorites from './MyFavorites'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export default compose(withRequiredLogin)(MyFavorites)
