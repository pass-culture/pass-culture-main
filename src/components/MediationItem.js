import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'

class MediationItem extends Component {
  render () {
    const { text,
      // tag
    } = this.props
    return (
      <div className='mediation-item flex items-center p1'>
        <Icon name='favorite-outline' />
        <div className='ml2'>
          { text }
        </div>
      </div>
    )
  }
}

export default connect(state =>
  ({ isEditing: Object.keys(state.form) > 0 })
)(MediationItem)
