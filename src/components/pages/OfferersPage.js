import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
import PageWrapper from '../layout/PageWrapper'
import OffererItem from '../OffererItem'
import Search from '../layout/Search'
import createOfferersSelector from '../../selectors/createOfferers'
import { requestData } from '../../reducers/data'

class OfferersPage extends Component {

  handleDataRequest = (handleSuccess, handleError) => {
    const {
      requestData,
    } = this.props
    requestData(
      'GET',
      'offerers',
      {
        handleSuccess,
        handleError,
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
        <h1 className="pc-title">
          Vos structures
        </h1>

        <p className="subtitle">
          Retrouvez ici la ou les structures dont vous gérez les offres Pass Culture.
        </p>

        <br />
        {false && (
          <nav className="level is-mobile">
            <Search
              collectionName="offerers"
              config={{
                isMergingArray: false,
                key: 'searchedOfferers'
              }}
              isLoading
            />
          </nav>
        )}
        <ul className="pc-list offerers-list">
          {offerers.map(o =>
            <OffererItem key={o.id} offerer={o} />)}
        </ul>
        <NavLink to={`/structures/nouveau`} className="button is-primary is-outlined">
          {false && <span className='icon'>
                    <Icon svg={'ico-guichet-w'} />
                  </span>}
          + Rattacher une structure
        </NavLink>
      </PageWrapper>
    )
  }
}

const offerersSelector = createOfferersSelector()

export default compose(
  connect(
    (state, ownProps) => ({
      offerers: offerersSelector(state)
    }), {
      requestData,
    })
)(OfferersPage)
