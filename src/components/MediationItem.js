import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'

class MediationItem extends Component {

  constructor () {
    super()
    this.state = {
      routePath: null,
      thumbUrl: null
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      id,
      occasionRoutePath
    } = nextProps
    return {
      routePath: `${occasionRoutePath}/accroches/${id}`,
      thumbUrl: `${THUMBS_URL}/mediations/${id}`
    }
  }

  render() {
    const {
      backText,
    } = this.props
    const {
      routePath,
      thumbUrl
    } = this.state
    return (
      <article className="mediation-item media box">
        <figure className="media-left">
          <p className="image is-96x96 is-2by3">
            <img alt='thumbnail' src={thumbUrl}/>
          </p>
        </figure>
        <div className="media-content">
          <div className="content">
            <Dotdotdot className='is-small' clamp={3}>
              {backText}
            </Dotdotdot>
          </div>
          <nav className="level is-mobile">
            <div className="level-left">
              <NavLink  to={routePath}>
                <button className="button is-primary level-item">
                  Modifier
                </button>
              </NavLink>
              <button className="button is-primary level-item"
                onClick={this.onDeactivateClick}>
                Effacer
              </button>
            </div>
          </nav>
        </div>
      </article>
    )
  }
}

export default MediationItem
