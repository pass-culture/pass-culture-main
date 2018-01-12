import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'

class SellerFavoriteItem extends Component {
  render () {
    const { description, tag } = this.props
    return (
      <div className='seller-favorite-item p3 mb2 relative'>
        <div className='seller-favorite-item__icon absolute'>
          <Icon name='favorite-outline' />
        </div>
        <div className='mt2 mb2'>
          { description }
          <div>
            {tag}
          </div>
        </div>
      </div>
    )
  }
}


export default connect(state =>
  ({ isEditing: Object.keys(state.form) > 0 })
)(SellerFavoriteItem)
