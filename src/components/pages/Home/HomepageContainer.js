/*
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { compose } from 'redux'

import { isFeatureActive } from '../../../store/features/selectors'

import Homepage from './Homepage'

const mapStateToProps = state => ({
  isPerfVenueStatsEnabled: isFeatureActive(state, 'PERF_VENUE_STATS'),
})

export default compose(connect(mapStateToProps))(Homepage)
