import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferModify from './OfferModify'
import { showModal } from '../reducers/modal'

class OfferItem extends Component {
  onClick = action => {
    const { showModal } = this.props
    showModal(<OfferModify {...this.props} />)
  }
  render () {
    const { description,
      id,
      isModify,
      name,
      work,
      thumbnailUrl
    } = this.props
    return (
      <div className={classnames(
        'offer-item flex items-center justify-between p1 mb1', {
          'offer-item--modify': isModify
        })}
        onClick={isModify && this.onClick}
      >
        <img alt='thumbnail'
          className='offer-item__image mr2'
          src={thumbnailUrl || work.thumbnailUrl}
        />
        <div className='offer-item__info flex-auto center'>
          <div className='h2 mb2'>
            {name}
          </div>
          <div>
            {description}
          </div>
        </div>
      </div>
    )
  }
}

export default connect(null, { showModal })(OfferItem)
