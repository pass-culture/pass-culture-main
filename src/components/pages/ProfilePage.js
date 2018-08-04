import PropTypes from 'prop-types'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Main from '../layout/Main'

class ProfilePage extends Component {
  componentWillReceiveProps(nextProps) {
    const {
      history: { push },
      user,
    } = nextProps
    if (user === false && this.props.user) {
      push('/')
    }
  }

  onSignOutClick = () => {
    const { dispatchRequestData } = this.props
    dispatchRequestData('GET', 'users/signout')
  }

  render() {
    const { user } = this.props
    return (
      <Main
        name="profile"
        footer={{ borderTop: true, colored: true }}
        backButton
      >
        <header>
Mon profil
        </header>
        <h2 className="title is-2">
Bienvenue !
        </h2>
        <button
          type="button"
          className="button is-default"
          disabled={!user}
          onClick={this.onSignOutClick}
        >
          Déconnexion
        </button>
      </Main>
    )
  }
}

ProfilePage.propTypes = {
  history: PropTypes.object.isRequired,
  dispatchRequestData: PropTypes.func.isRequired,
  user: PropTypes.object.isRequired,
}

export default compose(
  withRouter,
  connect(
    state => ({ user: state.user }),
    { dispatchRequestData: requestData }
  )
)(ProfilePage)
