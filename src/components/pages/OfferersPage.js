import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import OfferersList from '../OfferersList'
import SearchInput from '../layout/SearchInput'
import selectOfferers from '../../selectors/offerers'

class OfferersPage extends Component {

  componentDidMount () {
    this.handleRequestData()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData()
    }
  }

  handleRequestData = () => {
    const {
      requestData,
      user
    } = this.props
    user && requestData(
      'GET',
      'offerers',
      {
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
      location: { search },
        user,
        offerers
      } = this.props
    return (
      <PageWrapper name="profile"
        loading={!offerers}
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
            <SearchInput
              collectionNames={["offerers"]}
              config={{
                isMergingArray: false,
                key: 'searchedOfferers'
              }}
              isLoading
            />
          </nav>
        )}
        <OfferersList />
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


export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      offerers: selectOfferers(state, ownProps)
    }))
)(OfferersPage)
