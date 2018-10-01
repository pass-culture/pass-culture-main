import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'

import SearchPicture from './SearchPicture'
import selectTypeSublabels from '../../../selectors/selectTypeSublabels'

const NavByOfferType = ({ pagination, title, typeSublabels }) => (
  <div id="nav-by-offer-type">
    <h2 className="is-italic fs18">
      {title}
    </h2>
    {typeSublabels.map(typeSublabel => (
      <button
        key={typeSublabel}
        id="search-type-button"
        onClick={() =>
          pagination.change(
            { categories: typeSublabel },
            { pathname: '/recherche/resultats' }
          )
        }
        type="button"
      >
        <SearchPicture searchType={typeSublabel} />
        <label
          className="label fs22 is-medium is-white-text"
          id="search-type-label"
          htmlFor="search-type-checkbox"
        >
          {' '}
          {typeSublabel}
        </label>
      </button>
    ))}
  </div>
)

NavByOfferType.propTypes = {
  pagination: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

export default connect(state => ({
  typeSublabels: selectTypeSublabels(state),
}))(NavByOfferType)
