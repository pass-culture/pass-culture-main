import React from 'react'
import { compose } from 'redux'
import { Link } from 'react-router-dom'


import Icon from '../components/Icon'
import withLogin from '../hocs/withLogin'
import withSplash from '../hocs/withSplash'

const BetaPage = ({ errors }) => {
  return (
    <div className='page beta-page'>
      <h1><strong>Bienvenue</strong><strong>dans l'avant-première</strong><span>du Pass Culture</span></h1>
      <p>Et merci de votre participation pour nous aider à l'améliorer !</p>
      <footer>
        <Link to='/inscription'>
          C'est par là
          <Icon svg='ico-prev-w' />
        </Link>
      </footer>
    </div>
  )
}

export default compose(
  withLogin({ redirectTo: '/decouverte' }),
  withSplash({ triggerRemoveSplashTimeout: 2000 })
)(BetaPage)
