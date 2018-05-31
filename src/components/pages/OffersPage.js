import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import { withRouter } from 'react-router'
import { connect } from 'react-redux'

import OccasionsList from '../OccasionsList'
import withLogin from '../hocs/withLogin'
import SearchInput from '../layout/SearchInput'
import PageWrapper from '../layout/PageWrapper'
import { assignData, requestData } from '../../reducers/data'
import selectOccasions from '../../selectors/occasions'
import { collectionToPath } from '../../utils/translate'


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
      <PageWrapper name="offerer" loading={!occasions.length}>
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
        {occasions.length && <OccasionsList />}
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  withLogin({ isRequired: true }),
  connect(
    state => ({
      occasions: selectOccasions(state),
      user: state.user
    }),
    { assignData, requestData }
  )
)(OffersPage)
