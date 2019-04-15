import { connect } from 'react-redux'

import VenueProviderItem from './VenueProviderItem'
import mapStateToProps from './mapStateToProps'

export default connect(mapStateToProps)(VenueProviderItem)
