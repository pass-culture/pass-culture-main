import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'

import Matomo from './Matomo'

export const mapStateToProps = state => {
  const user = state.user

  console.log('USER ', user)

  return {
    user,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Matomo)
