import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypeSublabels'
import SearchPicture from './SearchPicture'

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
    const { filterParams, typeSublabels, title } = this.props

    const typesValue = decodeURI(filterParams.categories || '')

    return (
      <div id="filter-by-offer-types">
        <h2 className="fs18 is-italic is-uppercase text-center">
          {title}
        </h2>
        <div className="filter-menu-outer">
          {typeSublabels.map(typeSublabel => (
            <div className="filter-menu-inner" key={typeSublabel}>
              <SearchPicture searchType={typeSublabel} />
              <label id="type" className="fs20">
                {' '}
                {typeSublabel}
              </label>
              <input
                checked={typesValue.includes(typeSublabel)}
                onChange={() => this.onFilterChange(typeSublabel)}
                value={typeSublabel}
                type="checkbox"
              />
            </div>
          ))}
        </div>
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
