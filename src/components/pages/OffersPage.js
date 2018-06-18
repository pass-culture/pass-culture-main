import get from 'lodash.get'
import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import OccasionsList from '../OccasionsList'
import withLogin from '../hocs/withLogin'
import Icon from '../layout/Icon'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'
import { showModal } from '../../reducers/modal'
import selectOccasions from '../../selectors/occasions'


class OffersPage extends Component {
  handleRequestData = () => {
    const {
      history,
      requestData,
      showModal
    } = this.props
    requestData(
      'GET',
      'occasions',
      {
        handleSuccess: (state, action) =>
          !get(state, 'data.venues.length')
          && showModal(
            <div>
              Vous devez avoir déjà enregistré un lieu
              dans une de vos structures pour ajouter des offres
            </div>,
            {
              onCloseClick: () => history.push('/structures')
            }
          ),
        normalizer: {
          mediations: 'mediations',
          occurences: {
            key: 'eventOccurences',
            normalizer: {
              offer: 'offers',
              venue: 'venues'
            }
          },
          offers: {
            key: 'offers',
            normalizer: {
              'venue': 'venues'
            }
          }
        }
      }
    )
  }

  componentDidMount() {
    this.props.user && this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { user } = this.props
    if (user && user !== prevProps.user) {
      this.handleRequestData()
    }
  }

  render() {
    const {
      hasAtLeastOneVenue,
      occasions
    } = this.props

    return (
      <PageWrapper name="offers" loading={!occasions}>
        <div className="section">
          {
            hasAtLeastOneVenue && (
              <NavLink to={`/offres/evenements/nouveau`} className='button is-primary is-medium is-pulled-right'>
                <span className='icon'><Icon svg='ico-offres-r' /></span>
                <span>Créer une offre</span>
              </NavLink>
            )
          }
          <h1 className='pc-title'>
            Vos offres
          </h1>
          <p className="subtitle">
            Voici toutes vos offres apparaissant dans le Pass Culture.
          </p>
        </div>
        <div className='section'>

          <label className="label">Rechercher une offre :</label>
          <div className="field is-grouped">
            <p className="control is-expanded">
              <SearchInput
                collectionNames={["events", "things"]}
                config={{
                  isMergingArray: false,
                  key: 'searchedOccasions'
                }}
                isLoading
              />
            </p>
            <p className="control">
              <button className='button is-primary is-outlined is-medium'>OK</button>
              {' '}
              <button className='button is-secondary is-medium'>&nbsp;<Icon svg='ico-filter' />&nbsp;</button>
            </p>
          </div>
        </div>
        {
          <div className='section load-wrapper'>
            <OccasionsList />
          </div>
        }
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      hasAtLeastOneVenue: get(state, 'data.venues.length'),
      occasions: selectOccasions(state, ownProps),
      user: state.user
    }),
    { showModal }
  )
)(OffersPage)
