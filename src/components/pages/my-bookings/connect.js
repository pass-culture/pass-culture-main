import {
  selectSoonBookings,
  selectOtherBookings,
  selectRecommendations,
} from '../../../selectors'

export const mapStateToProps = state => {
  const recommendations = selectRecommendations(state)
  const otherBookings = selectOtherBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { otherBookings, recommendations, soonBookings }
}

export default mapStateToProps
