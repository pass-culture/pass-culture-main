import { compose } from 'redux'
import CsvTable from './CsvTable'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export default compose(withRequiredLogin)(CsvTable)
