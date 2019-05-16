import { selectSoonBookings, selectOtherBookings } from '../../../selectors'

export const mapStateToProps = state => {
  const otherBookings = selectOtherBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { otherBookings, soonBookings }
}

export default mapStateToProps
