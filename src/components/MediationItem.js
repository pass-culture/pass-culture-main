import get from 'lodash.get'
import React, { Component } from 'react'
import Dotdotdot from 'react-dotdotdot'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'

class MediationItem extends Component {
  render() {
    const { mediation, offer } = this.props
    const { backText, id } = mediation || {}
    const { routePath, thumbUrl } = this.state
    return (
      <article className="mediation-item media box">
        <figure className="media-left">
          <p className="image is-96x96">
            <img alt="thumbnail" src={`${THUMBS_URL}/mediations/${id}`} />
          </p>
        </figure>
        <div className="media-content">
          <div className="content">
            <Dotdotdot className="is-small" clamp={3}>
              {backText}
            </Dotdotdot>
          </div>
          <nav className="level is-mobile">
            <div className="level-left">
              <NavLink to={`/offers/${get(offer, 'id')}/accroches/${id}`}>
                <button className="button is-primary level-item">
                  Modifier
                </button>
              </NavLink>
              <button
                className="button is-primary level-item"
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
