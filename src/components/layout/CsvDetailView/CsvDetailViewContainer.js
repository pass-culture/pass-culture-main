import { compose } from 'redux'
import CsvDetailView from './CsvDetailView'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export default compose(
  withRequiredLogin,
)(CsvDetailView)
