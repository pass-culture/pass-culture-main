import PropTypes from 'prop-types'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Main from '../layout/Main'
import Footer from '../layout/Footer'

const renderPageHeader = () => (
  <header>
    {'Mon profil'}
  </header>
)

const renderPageFooter = () => {
  const footerProps = { borderTop: true, colored: true }
  return <Footer {...footerProps} />
}

class ProfilePage extends Component {
  componentWillReceiveProps(nextProps) {
    const { user } = this.props
    if (nextProps.user === false && user) {
      nextProps.history.push('/')
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
        backButton
        footer={renderPageFooter}
        header={renderPageHeader}
      >
        <h2 className="title is-2">
          {'Bienvenue !'}
        </h2>
        <button
          type="button"
          className="button is-default"
          disabled={!user}
          onClick={this.onSignOutClick}
        >
          {'Déconnexion'}
        </button>
      </Main>
    )
  }
}

ProfilePage.propTypes = {
  dispatchRequestData: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  user: PropTypes.object.isRequired,
}

export default compose(
  withRouter,
  connect(
    state => ({ user: state.user }),
    { dispatchRequestData: requestData }
  )
)(ProfilePage)
