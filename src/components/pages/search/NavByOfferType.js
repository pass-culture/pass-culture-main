import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypeSublabels'

const NavByOfferType = ({ handleQueryParamsChange, title, typeSublabels }) => (
  <div>
    <h2>
      {title}
    </h2>
    {typeSublabels.map(typeSublabel => (
      <div className="field checkbox" key={typeSublabel}>
        <label id="type" className="label">
          {' '}
          {typeSublabel}
        </label>
        <input
          id="type"
          className="input is-normal"
          onChange={() =>
            handleQueryParamsChange(
              { categories: typeSublabel },
              { pathname: '/recherche/resultats' }
            )
          }
          type="checkbox"
        />
      </div>
    ))}
  </div>
)

NavByOfferType.propTypes = {
  handleQueryParamsChange: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

export default connect(state => ({
  typeSublabels: selectTypeSublabels(state),
}))(NavByOfferType)
