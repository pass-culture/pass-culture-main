import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypes'
import SearchPicture from './SearchPicture'

class FilterByOfferTypes extends PureComponent {
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
      <div id="filter-by-offer-types" className="px12 pt20">
        <h2 className="fs15 is-italic is-uppercase text-center mb12">
          {title}
        </h2>
        <div className="pc-scroll-horizontal is-relative is-full-width">
          <div className="list flex-columns">
            {typeSublabels.map(typeSublabel => {
              const ischecked = typesValue.includes(typeSublabel)
              return (
                <label
                  key={typeSublabel}
                  className={`item p3 ${ischecked ? 'checked' : ''}`}
                >
                  <SearchPicture searchType={typeSublabel} />
                  <input
                    checked={ischecked}
                    className="is-hidden"
                    onChange={() => this.onChange(typeSublabel)}
                    value={typeSublabel}
                    type="checkbox"
                  />
                </label>
              )
            })}
          </div>
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
