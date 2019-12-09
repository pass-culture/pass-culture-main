import { connect } from 'react-redux'
import Results from './Results'

export const mapStateToProps = state => {
  const userLatitude = state.geolocation.latitude
  const userLongitude = state.geolocation.longitude

  return {
    userLatitude,
    userLongitude,
  }
}

export default connect(mapStateToProps)(Results)
