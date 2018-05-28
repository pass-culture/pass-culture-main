import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import { assignData, requestData } from '../../reducers/data'

import OccasionsList from '../OccasionsList'
import withLogin from '../hocs/withLogin'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'

class OffersPage extends Component {
  handleRequestData = () => {
    this.props.requestData('GET', `occasions`)
  }

  componentDidMount() {
    this.props.user && this.handleRequestData()
  }

  render() {
    return (
      <PageWrapper name="offerer" loading={!this.props.occasions.length}>
        <h1 className='title has-text-centered'>Vos offres</h1>
        <nav className="level is-mobile">
          <NavLink to={`/offres/evenements/nouveau`}>
            <button className="button is-primary level-item">
              Nouvel événement
            </button>
          </NavLink>
          <NavLink to={`/offres/objets/nouveau`}>
            <button className="button is-primary level-item">
              Nouvel objet
            </button>
          </NavLink>
        </nav>
        <nav className="level is-mobile">
          <SearchInput collectionNames={["events", "things"]} isLoading />
        </nav>
        {this.props.occasions.length && <OccasionsList />}
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    state => ({
      occasions: state.data.occasions || [],
      user: state.user
    }),
    { assignData, requestData }
  )
)(OffersPage)
