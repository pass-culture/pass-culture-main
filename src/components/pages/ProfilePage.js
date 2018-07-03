import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import { requestData } from '../../reducers/data'
import PageWrapper from '../layout/PageWrapper'

class ProfilePage extends Component {
  onSignOutClick = () => {
    const { requestData } = this.props
    requestData('GET', 'users/signout')
  }
  
  componentWillReceiveProps(nextProps) {
    const {
      history: { push },
      user,
    } = nextProps
    if (user === false && this.props.user) {
      push('/')
    }
  }


  render() {
    const { user } = this.props
    return (
      <PageWrapper
        name="profile"
        menuButton={{ borderTop: true, colored: true }}
        backButton
      >
        <header>Mon profil</header>
        <h2 className="title is-2">Bienvenue !</h2>
        <button
          className="button is-default"
          disabled={!user}
          onClick={this.onSignOutClick}
        >
          Déconnexion
        </button>
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter,
  connect(state => ({ user: state.user }), { requestData })
)(ProfilePage)
