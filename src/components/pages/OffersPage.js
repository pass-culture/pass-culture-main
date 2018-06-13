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
import selectOccasions from '../../selectors/occasions'


class OffersPage extends Component {
  handleRequestData = () => {
    this.props.requestData('GET', 'occasions')
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
    const { occasions } = this.props
    return (
      <PageWrapper name="offers" loading={!occasions.length}>
        <div className="section">
          <NavLink to={`/offres/evenements/nouveau`} className='button is-primary is-medium is-pulled-right'>
            + Ajouter une offre
          </NavLink>
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
        {occasions.length && <div className='section'><OccasionsList /></div>}
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
    })
  )
)(OffersPage)
