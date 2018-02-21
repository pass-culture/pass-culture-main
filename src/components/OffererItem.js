import React, { Component } from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withFrontendOfferer from '../hocs/withFrontendOfferer'

class OffererItem extends Component {
  onClick = () => {
    const { id, history } = this.props
    history.push(`/pro/${id}`)
  }
  render () {
    const {
      name,
      thumbUrl
    } = this.props
    return (
      <button className='offerer-item button button--alive button--inversed mb1 mr2 center'
        onClick={this.onClick}>
        <img alt='thumbnail'
          className='offerer-item__image'
          src={thumbUrl} />
        <div>
          {name}
        </div>
      </button>
    )
  }
}

export default compose(
  withRouter,
  withFrontendOfferer
)(OffererItem)
