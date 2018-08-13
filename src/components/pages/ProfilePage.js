import PropTypes from 'prop-types'
import { requestData } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

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

class ProfilePage extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { requestData }
    this.actions = bindActionCreators(actions, dispatch)
  }

  componentWillReceiveProps(nextProps) {
    const { user } = this.props
    if (nextProps.user === false && user) {
      nextProps.history.push('/')
    }
  }

  onSignOutClick = () => {
    this.actions.requestData('GET', 'users/signout')
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
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  user: PropTypes.object.isRequired,
}

const mapStateToProps = state => ({ user: state.user })

export default connect(mapStateToProps)(ProfilePage)
