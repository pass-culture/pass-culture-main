import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Header from './Header'

export const mapStateToProps = state => {
  const { data } = state
  const user = selectCurrentUser(state)
  const { publicName: name } = user
  const { offerers } = data

  return {
    name,
    offerers,
  }
}

export default compose(withRouter, connect(mapStateToProps))(Header)
