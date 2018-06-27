import get from 'lodash.get'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import OccasionItem from '../OccasionItem'
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

  handleDataRequest = (handleSuccess, handleError) => {
    const {
      lieu,
      requestData,
      structure,
      user
    } = this.props
    let apiPath = 'occasions'
    if (lieu) {
      apiPath = `${apiPath}?venueId=${lieu}`
    } else if (structure) {
      apiPath = `${apiPath}?offererId=${structure}`
    }
    user && requestData(
      'GET',
      apiPath,
      {
        handleSuccess,
        handleError,
        normalizer: occasionNormalizer
      }
    )
    requestData('GET', 'types')
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
                  Structure: <span className="is-medium"> {offerer.name} </span>
                </p>
              )
              : venue && (
                <p>
                  Lieu: <span className="is-medium"> {venue.name} </span>
                </p>
              )
          }
        </div>

        {
          <div className='section load-wrapper'>
            <ul className='occasions-list pc-list'>
              {
                occasions.map(o =>
                  <OccasionItem key={o.id} occasion={o} />)
              }
            </ul>
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
      const { structure, lieu } = searchSelector(state, ownProps.location.search)
      return {
        lieu,
        occasions: occasionsSelector(state, structure, lieu),
        offerer: offererSelector(state, structure),
        structure,
        user: state.user,
        venue: venueSelector(state, lieu)
      }
    },
    { showModal, requestData }
  )
)(OccasionsPage)
