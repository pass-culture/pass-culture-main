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
import { occasionNormalizer } from '../../utils/normalizers'


class OccasionsPage extends Component {

  handleRequestData = () => {
    const {
      requestData,
      user
    } = this.props
    user && requestData(
      'GET',
      'occasions',
      {
        normalizer: occasionNormalizer
      }
    )
  }

  componentDidMount() {
    this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { user } = this.props
    if (user !== prevProps.user) {
      this.handleRequestData()
    }
  }

  render() {
    const {
      occasions
    } = this.props

    return (
      <PageWrapper name="offers" loading={!occasions}>
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

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      occasions: selectOccasions(state, ownProps),
      user: state.user
    }),
    { showModal }
  )
)(OccasionsPage)
