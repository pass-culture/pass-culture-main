import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import selectThumbUrl from '../selectors/thumbUrl'
import { THUMBS_URL } from '../utils/config'

class OffererItem extends Component {
  onClick = () => {
    const { id, history } = this.props
    history.push(`/gestion/${id}`)
  }
  render() {
    const { id, name } = this.props
    return (
      <a className="tile is-parent" onClick={this.onClick}>
        <article className="media tile is-child box">
          <p className="title">{name}</p>
          <figure className="image is-4by3">
            <img alt="thumbnail" src={`${THUMBS_URL}/offerers/${id}`} />
          </figure>
        </article>
      </a>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({
      // thumbUrl: selectThumbUrl(state)
    })
  )
)(OffererItem)
