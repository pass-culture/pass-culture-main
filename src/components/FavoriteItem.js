import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'

class FavoriteItem extends Component {
  render () {
    const { comment,
      // tag
    } = this.props
    return (
      <div className='favorite-item flex items-center p1'>
        <Icon name='favorite-outline' />
        <div className='ml2'>
          { comment }
        </div>
      </div>
    )
  }
}

export default connect(state =>
  ({ isEditing: Object.keys(state.form) > 0 })
)(FavoriteItem)
