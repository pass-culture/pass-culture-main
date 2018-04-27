import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffererForm from './OffererForm'
import Icon from '../layout/Icon'
import { showModal } from '../../reducers/modal'

class OffererEditButton extends Component {
  onClick = () => {
    const { showModal } = this.props
    showModal(<OffererForm />)
  }
  render() {
    const { offerer } = this.props
    return (
      <button
        className='button is-default'
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
