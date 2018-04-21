import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import OffererForm from './OffererForm'
import { showModal } from '../reducers/modal'

class OffererEditButton extends Component {
  onClick = () => {
    const { showModal } = this.props
    showModal(<OffererForm />)
  }
  render() {
    const { offerer } = this.props
    return (
      <button
        className={classnames('button button--alive button--rounded', {
          'button--disabled': !offerer,
        })}
        disabled={!offerer}
        onClick={this.onClick}
      >
        <Icon name="perm-data-setting" />
      </button>
    )
  }
}

export default connect(
  state => ({ offerer: state.user && state.user.offerer }),
  { showModal }
)(OffererEditButton)
