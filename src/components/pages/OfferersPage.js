import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import OffererItem from '../OffererItem'
import SearchInput from '../layout/SearchInput'
import createOfferersSelector from '../../selectors/createOfferers'

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
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      offerers: offerersSelector(state)
    }))
)(OfferersPage)
