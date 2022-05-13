import ActionsBar from './ActionsBar'
import { connect } from 'react-redux'
import { showNotification } from 'store/reducers/notificationReducer'

export const mapStateToProps = state => {
  return {
    searchFilters: state.offers.searchFilters,
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    showSuccessNotification: text =>
      dispatch(
        showNotification({
          type: 'success',
          text,
        })
      ),
    showPendingNotification: text =>
      dispatch(
        showNotification({
          type: 'pending',
          text,
        })
      ),
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(ActionsBar)
