import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import Icon from '../layout/Icon'
import PageWrapper from '../layout/PageWrapper'
import withLogin from '../hocs/withLogin'
import { closeSplash } from '../../reducers/splash'
import { DEFAULT_TO } from '../../utils/config'

class BetaPage extends Component {
  componentDidMount() {
    const { closeSplash, closeSplashTimeout } = this.props
    setTimeout(closeSplash, closeSplashTimeout)
  }

  render() {
    const { user } = this.props
    return (
      <PageWrapper name="beta" fullscreen redBg>
        <h1>
          <strong>Bienvenue dans la version beta</strong>{ ' ' }
          <span>du Pass Culture pour les Professionels</span>
        </h1>
        <p>Et merci de votre participation pour nous aider à l'améliorer !</p>
        <footer>
          <Link
            to={user ? "/offres" : "/inscription"}
            className="button is-secondary is-inversed has-text-weight-light is-italic"
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
  withLogin({ redirectTo: DEFAULT_TO }),
  connect(state => ({ closeSplashTimeout: state.splash.closeTimeout }), {
    closeSplash,
  })
)(BetaPage)
