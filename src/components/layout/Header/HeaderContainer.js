import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Header from './Header'

export const mapStateToProps = state => {
  const { user, data } = state
  const { publicName: name } = user
  const { offerers } = data

  return {
    name,
    offerers,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Header)
