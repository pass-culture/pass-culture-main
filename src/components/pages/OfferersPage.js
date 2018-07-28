import {
  requestData
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import PageWrapper from '../layout/PageWrapper'
import OffererItem from '../OffererItem'
import Search from '../layout/Search'
import offerersSelector from '../../selectors/offerers'

class OfferersPage extends Component {

  handleDataRequest = (handleSuccess, handleFail) => {
    const {
      requestData,
    } = this.props
    requestData(
      'GET',
      'offerers',
      {
        handleSuccess,
        handleFail,
        normalizer: {
          managedVenues: {
            key: 'venues',
            normalizer: {
              eventOccurences: {
                key: 'eventOccurences',
                normalizer: {
                  event: 'occasions'
                }
              }
            }
          }
        }
      }
    )
  }

  render () {

    const {
        offerers
      } = this.props
    return (
      <PageWrapper name="offerers"
        handleDataRequest={this.handleDataRequest}
      >
        <h1 className="main-title">
          Vos structures
        </h1>

        <p className="subtitle">
          Retrouvez ici la ou les structures dont vous gérez les offres Pass Culture.
        </p>

        <br />
        <NavLink to={`/structures/nouveau`} className="button is-primary is-outlined">
          + Rattacher une structure
        </NavLink>

        <br />
        <br />
        <br />
        <ul className="main-list offerers-list">
          {offerers.map(o =>
            <OffererItem key={o.id} offerer={o} />)}
        </ul>
      </PageWrapper>
    )
  }
}

export default compose(
  connect(
    (state, ownProps) => ({
      offerers: offerersSelector(state)
    }), {
      requestData,
    })
)(OfferersPage)
