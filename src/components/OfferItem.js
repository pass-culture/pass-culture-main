import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import MediationItem from './MediationItem'
import OfferModify from './OfferModify'
import PriceItem from './PriceItem'
import { assignData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { showModal } from '../reducers/modal'

class OfferItem extends Component {
  onCloseClick = () => {
    const { assignData, resetForm } = this.props
    assignData({ work: null })
    resetForm()
  }
  onClick = action => {
    const { onCloseClick } = this
    const { showModal } = this.props
    showModal(<OfferModify {...this.props} />, { onCloseClick })
  }
  render() {
    const {
      description,
      isMediations,
      isModify,
      isPrices,
      maxDescriptionLength,
      mediations,
      name,
      prices,
      thumbUrl,
    } = this.props
    console.log('mediations', mediations)
    return (
      <div
        className={classnames('offer-item', {
          modify: isModify,
        })}
        onClick={isModify && this.onClick}
      >
        <img alt="thumbnail" src={thumbUrl} />
        <div className="content">
          <h2 className="title is-2">{name}</h2>
          <div className="description">
            {description && description.length > maxDescriptionLength
              ? `${description.slice(0, maxDescriptionLength)}...`
              : description}
          </div>
          <div>
            <div>
              {isPrices &&
                prices &&
                prices.map((price, index) => (
                  <PriceItem key={index} {...price} />
                ))}
            </div>
            <div>
              {isMediations &&
                mediations &&
                mediations.map((mediation, index) => (
                  <MediationItem key={index} {...mediation} />
                ))}
            </div>
          </div>
        </div>
      </div>
    )
  }
}

OfferItem.defaultProps = {
  maxDescriptionLength: 300,
}

export default connect(null, { assignData, resetForm, showModal })(OfferItem)
