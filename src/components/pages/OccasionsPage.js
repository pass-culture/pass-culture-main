import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import OccasionItem from '../OccasionItem'
import InfiniteScroller from '../layout/InfiniteScroller'
import Icon from '../layout/Icon'
import Search from '../layout/Search'
import PageWrapper from '../layout/PageWrapper'
import { showModal } from '../../reducers/modal'
import { requestData } from '../../reducers/data'
import createOccasionsSelector from '../../selectors/createOccasions'
import createOffererSelector from '../../selectors/createOfferer'
import createSearchSelector from '../../selectors/createSearch'
import createVenueSelector from '../../selectors/createVenue'
import { occasionNormalizer } from '../../utils/normalizers'

class OccasionsPage extends Component {

  handleDataRequest = (handleSuccess, handleFail, page=1) => {
    const {
      offererId,
      requestData,
      user,
      types,
      venueId
    } = this.props
    let apiPath = 'occasions?'
    if (venueId) {
      apiPath = `${apiPath}?venueId=${venueId}`
    } else if (offererId) {
      apiPath = `${apiPath}?offererId=${offererId}`
    }
    user && requestData(
      'GET',
      `${apiPath}&page=${page}`,
      {
        handleSuccess,
        handleFail,
        normalizer: occasionNormalizer
      }
    )
    types.length === 0 && requestData('GET', 'types')
  }

  render() {
    const {
      occasions,
      offerer,
      venue
    } = this.props

    return (
      <PageWrapper name="offers" handleDataRequest={this.handleDataRequest}>
        <div className="section">
          <NavLink to={`/offres/nouveau`} className='button is-primary is-medium is-pulled-right'>
            <span className='icon'><Icon svg='ico-offres-w' /></span>
            <span>Créer une offre</span>
          </NavLink>
          <h1 className='pc-title'>
            Vos offres
          </h1>
        </div>
        <div className='section'>
          <label className="label">Rechercher une offre :</label>
          <Search collectionName="occasions"
                  config={{
                    isMergingArray: false,
                    key: 'searchedOccasions'
                  }}
          />
        </div>

        <div className='section'>
          {
            offerer
              ? (
                <p>
                  Structure: <span className="has-text-weight-semibold"> {offerer.name} </span>
                </p>
              )
              : venue && (
                <p>
                  Lieu: <span className="has-text-weight-semibold"> {venue.name} </span>
                </p>
              )
          }
        </div>

        {
          <div className='section'>
            <InfiniteScroller className='occasions-list pc-list' handleLoadMore={this.handleDataRequest}>
              { occasions.map(o =>
                <OccasionItem key={o.id} occasion={o} />
              )}
            </InfiniteScroller>
          </div>
        }
      </PageWrapper>
    )
  }
}


const occasionsSelector = createOccasionsSelector()
const offererSelector = createOffererSelector()
const searchSelector = createSearchSelector()
const venueSelector = createVenueSelector()

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { offererId, venueId } = searchSelector(state, ownProps.location.search)
      return {
        occasions: occasionsSelector(state, offererId, venueId),
        offerer: offererSelector(state, offererId),
        offererId,
        user: state.user,
        types: state.data.types,
        venue: venueSelector(state, venueId),
        venueId
      }
    },
    { showModal, requestData }
  )
)(OccasionsPage)
