import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import SearchPicture from './SearchPicture'

class FilterByOfferTypes extends PureComponent {
  onChangeCategory = category => () => {
    const { filterActions, filterState } = this.props
    const typesValue = decodeURI(filterState.params.categories || '')
    const isAlreadyIncluded = typesValue.includes(category)

    if (isAlreadyIncluded) {
      filterActions.remove('categories', category)
      return
    }

    filterActions.add('categories', category)
  }

  render() {
    const { filterState, typeSublabels } = this.props
    const typesValue = decodeURI(filterState.params.categories || '')

    return (
      <div
        className="pt18"
        id="filter-by-offer-types"
      >
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">{'Quoi'}</h2>
        <div className="pc-scroll-horizontal is-relative">
          <div className="pc-list flex-columns pt7">
            {typeSublabels.map((category, index) => {
              const isChecked = typesValue.includes(category)
              const className = isChecked ? 'checked' : ''
              const inputId = `search-image-checkbox-${index}`

              return (
                <label
                  className={`item p3 is-relative ${className}`}
                  htmlFor={inputId}
                  key={category}
                >
                  <SearchPicture category={category} />
                  <input
                    checked={isChecked}
                    className="is-hidden"
                    id={inputId}
                    onChange={this.onChangeCategory(category)}
                    type="checkbox"
                    value={category}
                  />
                  {isChecked && (
                    <span className="icon-container is-absolute">
                      <span className="is-relative">
                        <i className="icon-legacy-check-circled" />
                      </span>
                    </span>
                  )}
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
  filterActions: PropTypes.shape({
    add: PropTypes.func.isRequired,
    change: PropTypes.func.isRequired,
    remove: PropTypes.func.isRequired,
  }).isRequired,
  filterState: PropTypes.shape({
    isNew: PropTypes.bool,
    params: PropTypes.shape({
      categories: PropTypes.string,
      date: PropTypes.string,
      distance: PropTypes.string,
      jours: PropTypes.string,
      latitude: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      longitude: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      'mots-cles': PropTypes.string,
      orderBy: PropTypes.string,
    }),
  }).isRequired,
  typeSublabels: PropTypes.arrayOf(PropTypes.string).isRequired,
}

export default FilterByOfferTypes
