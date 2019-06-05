import { connect } from 'react-redux'

import { FilterByDistance } from './FilterByDistance'

const mapStateToProps = state => ({
  geolocation: state.geolocation,
})

export const FilterByDistanceContainer = connect(mapStateToProps)(
  FilterByDistance
)
