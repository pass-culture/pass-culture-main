import get from 'lodash.get'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import CancelThisLink from './CancelThisLink'

export const mapStateToProps = (state, props) => {
  const { booking, history } = props
  const priceValue = get(booking, 'stock.price')
  const isCancelled = get(booking, 'isCancelled')

  return {
    history,
    isCancelled,
    priceValue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(CancelThisLink)
