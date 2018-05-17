import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import Icon from '../layout/Icon'
import PageWrapper from '../layout/PageWrapper'
import withLogin from '../hocs/withLogin'
import { closeSplash } from '../../reducers/splash'

class BetaPage extends Component {
  componentDidMount() {
    const { closeSplash, closeSplashTimeout } = this.props
    setTimeout(closeSplash, closeSplashTimeout)
  }

  render() {
    return (
      <PageWrapper name="beta" redBg>
        <h1>
          <strong>Bienvenue dans la version beta</strong>
          <span>du Pass Culture</span>
        </h1>
        <p>Et merci de votre participation pour nous aider à l'améliorer !</p>
        <footer>
          <Link
            to="/inscription"
            className="button is-secondary has-text-weight-light is-italic"
          >
            C'est par là
            <Icon svg="ico-next" />
          </Link>
        </footer>
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ redirectTo: '/decouverte' }),
  connect(state => ({ closeSplashTimeout: state.splash.closeTimeout }), {
    closeSplash,
  })
)(BetaPage)
