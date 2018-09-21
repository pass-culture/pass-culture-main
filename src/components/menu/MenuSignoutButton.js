/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose, bindActionCreators } from 'redux'
import { Icon, requestData } from 'pass-culture-shared'

import { toggleMainMenu } from '../../reducers/menu'

class MenuSignoutButton extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = this.props
    const actions = { requestData, toggleMainMenu }
    this.actions = bindActionCreators(actions, dispatch)
  }

  onHandleSuccess = () => {
    const { history } = this.props
    history.push('/connexion')
    this.actions.toggleMainMenu()
  }

  onSignOutClick = () => {
    const route = 'users/signout'
    const opts = { handleSuccess: this.onHandleSuccess }
    this.actions.requestData('GET', route, opts)
  }

  render() {
    return (
      <button
        type="button"
        id="main-menu-logout-button"
        className="pc-text-button flex-columns text-left p16"
        onClick={this.onSignOutClick}
      >
        <span className="menu-icon mr16 text-center">
          <Icon svg="ico-deconnect-w" alt="" />
        </span>
        <span>Déconnexion</span>
      </button>
    )
  }
}

MenuSignoutButton.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
}

export default compose(
  withRouter,
  connect()
)(MenuSignoutButton)
