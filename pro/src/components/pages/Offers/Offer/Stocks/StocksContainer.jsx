import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotification } from 'store/reducers/notificationReducer'

import Stocks from './Stocks'

const mapDispatchToProps = dispatch => ({
  showErrorNotification: () =>
    dispatch(
      showNotification({
        type: 'error',
        text: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
      })
    ),
  showSuccessNotification: text =>
    dispatch(
      showNotification({
        type: 'success',
        text,
      })
    ),
  showHtmlErrorNotification: text =>
    dispatch(
      showNotification({
        type: 'error',
        text,
      })
    ),
})

export default compose(withRouter, connect(null, mapDispatchToProps))(Stocks)
