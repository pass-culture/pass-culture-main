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
import { requestData } from '../../reducers/data'
import createSearchSelector from '../../selectors/createSearch'
import createOccasionsSelector from '../../selectors/createOccasions'
import { occasionNormalizer } from '../../utils/normalizers'

class OccasionsPage extends Component {

  handleDataRequest = (handleSuccess, handleError) => {
    const {
      requestData,
      user
    } = this.props
    user && requestData(
      'GET',
      'occasions',
      {
        handleSuccess,
        handleError,
        normalizer: occasionNormalizer
      }
    )
  }

  // componentDidMount() {
  //   this.handleDataRequest()
  // }

  // componentDidUpdate(prevProps) {
  //   const { user } = this.props
  //   if (user !== prevProps.user) {
  //     this.handleDataRequest()
  //   }
  // }

  render() {
    const {
      occasions
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

const searchSelector = createSearchSelector()
const occasionsSelector = createOccasionsSelector(searchSelector)

export default compose(
  withRouter,
  // withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => {
      const { offererId, venueId } = searchSelector(state, ownProps.location.search)
      return {
        occasions: occasionsSelector(state, offererId, venueId),
        user: state.user
      }
    },
    { showModal, requestData }
  )
)(OccasionsPage)
