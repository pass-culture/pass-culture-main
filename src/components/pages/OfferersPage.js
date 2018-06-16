import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { NavLink } from 'react-router-dom'

import Icon from '../layout/Icon'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import OfferersList from '../OfferersList'
import SearchInput from '../layout/SearchInput'
import selectOfferers from '../../selectors/offerers'

const OfferersPage = ({
  location: { search },
  user,
  offerers
}) => {

  const notification = search === '?success=true' && {
    text: 'Le rattachement de la structure a été demandé. Vous allez recevoir la dernière étape d\'inscription par e-mail.',
    type: 'success'
  }

  return (
    <PageWrapper name="profile"
      loading={!offerers}
      notification={notification}
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


export default compose(
  withLogin({ isRequired: true }),
  connect(
    (state, ownProps) => ({
      offerers: selectOfferers(state, ownProps)
    }))
)(OfferersPage)
