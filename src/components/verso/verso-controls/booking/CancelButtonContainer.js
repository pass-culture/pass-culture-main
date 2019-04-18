import get from 'lodash.get'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import CancelButton from './CancelButton'

export const mapStateToProps = (state, props) => {
  const { booking, history, location } = props
  const locationSearch = location.search
  const priceValue = get(booking, 'stock.price')
  const isCancelled = get(booking, 'isCancelled')
  return {
    history,
    isCancelled,
    locationSearch,
    priceValue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(CancelButton)
