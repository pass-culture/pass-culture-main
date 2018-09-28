import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypeSublabels'
import SearchPicture from './SearchPicture'

class FilterByOfferTypes extends Component {
  onChange = typeSublabel => {
    const { filter } = this.props

    const typesValue = decodeURI(filter.query.categories || '')

    const isAlreadyIncluded = typesValue.includes(typeSublabel)

    if (isAlreadyIncluded) {
      filter.remove('categories', typeSublabel)
      return
    }

    filter.add('categories', typeSublabel)
  }

  render() {
    const { filter, typeSublabels, title } = this.props

    const typesValue = decodeURI(filter.query.categories || '')

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
                onChange={() => this.onChange(typeSublabel)}
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
  filter: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

export default connect(state => ({
  typeSublabels: selectTypeSublabels(state),
}))(FilterByOfferTypes)
