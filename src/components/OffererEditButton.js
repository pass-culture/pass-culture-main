import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import OffererSetting from './OffererSetting'
import { showModal } from '../reducers/modal'

class OffererEditButton extends Component {
  onClick = () => {
    const { showModal } = this.props
    showModal(<OffererSetting />)
  }
  render () {
    return (
      <button className='button button--alive button--rounded'
        onClick={this.onClick} >
        <Icon name='perm-data-setting' />
      </button>
    )
  }
}

export default connect(null, { showModal })(OffererEditButton)
