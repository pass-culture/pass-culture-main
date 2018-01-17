import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferModify from './OfferModify'
import PriceItem from './PriceItem'
import { assignData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { showModal } from '../reducers/modal'
import { API_URL } from '../utils/config'

class OfferItem extends Component {
  onCloseClick = () => {
    const { assignData, resetForm } = this.props
    console.log('qsqsqs')
    assignData({ work: null })
    resetForm()
  }
  onClick = action => {
    const { onCloseClick } = this
    const { showModal } = this.props
    showModal(<OfferModify {...this.props} />, { onCloseClick })
  }
  render () {
    const { description,
      isModify,
      isPrices,
      name,
      prices,
      sellersFavorites,
      work,
      thumbnailUrl
    } = this.props
    console.log('prices', prices)
    console.log('sellersFavorites', sellersFavorites)
    return (
      <div className={classnames(
        'offer-item flex items-center justify-between p1 mb1', {
          'offer-item--modify': isModify
        })}
        onClick={isModify && this.onClick}
      >
        <img alt='thumbnail'
          className='offer-item__image mr2'
          src={thumbnailUrl || `${API_URL}/thumbs/${work.id}`}
        />
        <div className='offer-item__info flex-auto center'>
          <div className='h2 mb2'>
            {name}
          </div>
          <div className='mb2'>
            {description}
          </div>
          {
            isPrices && prices && prices.map((price, index) => <PriceItem key={index} />)
          }
        </div>
      </div>
    )
  }
}

export default connect(null,
  { assignData, resetForm, showModal }
)(OfferItem)
