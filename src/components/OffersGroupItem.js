import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferModify from './OfferModify'
import { assignData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { showModal } from '../reducers/modal'

class OffersGroupItem extends Component {
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
      isMediations,
      isModify,
      isPrices,
      offers
    } = this.props
    const groupingSource = offers[0].source
    return (
      <article className="media">
        <figure className="media-left">
          <p className="image is-64x64">
            <img src={groupingSource.thumbUrl}/>
          </p>
        </figure>
        <div className="media-content">
          <div className="content">
            <p>
              <strong>{groupingSource.name}</strong>
            </p>
          </div>
          <nav className="level is-mobile">
            <div className="level-left">
              <a className="level-item">
                <span className="icon is-small"><i className="fas fa-reply"></i></span>
              </a>
              <a className="level-item">
                <span className="icon is-small"><i className="fas fa-retweet"></i></span>
              </a>
              <a className="level-item">
                <span className="icon is-small"><i className="fas fa-heart"></i></span>
              </a>
            </div>
          </nav>
        </div>
        <div className="media-right">
          <button className="delete"></button>
        </div>
      </article>
    )
  }
}

OffersGroupItem.defaultProps = {
  maxDescriptionLength: 300,
}

export default connect(
  null,
  { assignData, resetForm, showModal }
)(OffersGroupItem)
