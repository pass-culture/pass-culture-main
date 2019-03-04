import { assignData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import SearchPicture from './SearchPicture'

const NavByOfferType = ({ dispatch, query, title, typeSublabels }) => (
  <div id="nav-by-offer-type">
    <h2 className="is-italic fs15">
      {title}
    </h2>
    <div className="pc-list flex-columns wrap-2">
      {typeSublabels.map(typeSublabel => (
        <button
          id="button-nav-by-offer-type"
          key={typeSublabel}
          onClick={() => {
            dispatch(assignData({ recommendations: [] }))
            query.change(
              { categories: typeSublabel, page: null },
              { pathname: `/recherche/resultats/${typeSublabel}` }
            )
          }}
          type="button"
          className="item no-border no-background no-outline mt12 col-1of2"
        >
          <SearchPicture searchType={typeSublabel} />
        </button>
      ))}
    </div>
  </div>
)

NavByOfferType.propTypes = {
  dispatch: PropTypes.func.isRequired,
  query: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

export default compose(
  withQueryRouter,
  connect()
)(NavByOfferType)
