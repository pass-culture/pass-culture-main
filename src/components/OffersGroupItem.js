import Dotdotdot from 'react-dotdotdot'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { NavLink, withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { assignData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { showModal } from '../reducers/modal'
import selectOfferer from '../selectors/offerer'

class OffersGroupItem extends Component {
  onDeleteClick = () => {

  }

  render() {
    const {
      match: { params: { offererId } },
      offers
    } = this.props
    const groupingOffer = offers[0]
    // const groupingEventOccurence = groupingOffer.eventOccurence
    const groupingSource = groupingOffer.source
    // console.log('offerer', offerer, groupingSource, groupingOffer)
    return (
      <article className="offers-group-item media">
        <figure className="media-left">
          <p className="image is-96x96 is-2by3">
            <img alt='thumbnail' src={groupingSource.thumbUrl}/>
          </p>
        </figure>
        <div className="media-content">
          <div className="content">
            <p className='title'>
              <strong>{groupingSource.name}</strong>
            </p>
            <Dotdotdot className='is-small' clamp={3}>
              {groupingSource.description}
            </Dotdotdot>
          </div>
          <nav className="level is-mobile">
            <div className="level-left">
              <NavLink  to={`/gestion/${offererId}/${groupingOffer.id}`}>
                <button className="button is-primary level-item">
                  Modifier
                </button>
              </NavLink>
              <button className="button is-primary level-item"
                onClick={this.onDeleteClick}>
                Supprimer
              </button>
            </div>
          </nav>
        </div>
      </article>
    )
  }
}

OffersGroupItem.defaultProps = {
  maxDescriptionLength: 300,
}

export default compose(
  withRouter,
  connect(
    () => (state, ownProps) => ({ offerer: selectOfferer(state, ownProps) }),
    { assignData, resetForm, showModal }
  )
)(OffersGroupItem)
