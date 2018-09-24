import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypeSublabels'

class FilterByOfferTypes extends Component {
  onFilterChange = typeSublabel => {
    const {
      handleFilterParamAdd,
      handleFilterParamRemove,
      filterParams,
    } = this.props

    const typesValue = decodeURI(filterParams.categories || '')

    const isAlreadyIncluded = typesValue.includes(typeSublabel)

    if (isAlreadyIncluded) {
      handleFilterParamRemove('categories', typeSublabel)
      return
    }

    handleFilterParamAdd('categories', typeSublabel)
  }

  render() {
    const { filterParams, title, typeSublabels } = this.props

    const typesValue = decodeURI(filterParams.categories || '')

    return (
      <div>
        <h2>
          {title}
        </h2>
        {typeSublabels.map(typeSublabel => (
          <div className="field field-checkbox" key={typeSublabel}>
            <label id="type" className="label">
              {' '}
              {typeSublabel}
            </label>
            <input
              checked={typesValue.includes(typeSublabel)}
              className="input is-normal"
              onChange={() => this.onFilterChange(typeSublabel)}
              value={typeSublabel}
              type="checkbox"
            />
          </div>
        ))}
      </div>
    )
  }
}

FilterByOfferTypes.propTypes = {
  filterParams: PropTypes.object.isRequired,
  handleFilterParamAdd: PropTypes.func.isRequired,
  handleFilterParamRemove: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

export default connect(state => ({
  typeSublabels: selectTypeSublabels(state),
}))(FilterByOfferTypes)
