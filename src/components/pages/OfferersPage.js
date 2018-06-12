import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import OfferersList from '../OfferersList'
import SearchInput from '../layout/SearchInput'

const OfferersPage = ({ user, offerers }) => {
  return (
    <PageWrapper name="profile" loading={!offerers} notification={offerers && offerers.length === 1 && !offerers[0].isActive && {
      type: 'success',
      text: 'Le rattachement de la structure a été demandé. Vous allez recevoir la dernière étape d\'inscription par e-mail.'
    }}>
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


export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      offerers: state.data.offerers
    }))
)(OfferersPage)
