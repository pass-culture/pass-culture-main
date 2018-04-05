import React, { Component } from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { Link } from 'react-router-dom'


import Icon from '../components/Icon'

const inputClassName = 'input block col-12 mb2'

class BetaPage extends Component {
  render () {
    const { errors } = this.props
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
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({}),
    {}
  ))(BetaPage)
