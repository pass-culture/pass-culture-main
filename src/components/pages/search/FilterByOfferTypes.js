import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypes'
import SearchPicture from './SearchPicture'

class FilterByOfferTypes extends PureComponent {
  onChangeType = category => () => {
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
    const { filterState, typeSublabels, title } = this.props
    const typesValue = decodeURI(filterState.params.categories || '')

    return (
      <div className="pt18" id="filter-by-offer-types">
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
          {title}
        </h2>
        <div className="pc-scroll-horizontal is-relative">
          <div className="pc-list flex-columns pt7">
            {typeSublabels.map((category, index) => {
              const ischecked = typesValue.includes(category)
              const className = ischecked ? 'checked' : ''
              const inputId = `search-image-checkbox-${index}`

              return (
                <label
                  className={`item p3 is-relative ${className}`}
                  htmlFor={inputId}
                  key={category}
                >
                  <SearchPicture searchType={category} />
                  <input
                    checked={ischecked}
                    className="is-hidden"
                    id={inputId}
                    onChange={this.onChangeType(category)}
                    type="checkbox"
                    value={category}
                  />
                  {ischecked && (
                    <span className="icon-container is-absolute">
                      <span className="icon-container-inner is-relative">
                        <i className="icon-ico-check" />
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
  filterActions: PropTypes.object.isRequired,
  filterState: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

const mapStateToProps = state => ({
  typeSublabels: selectTypeSublabels(state),
})

export default connect(mapStateToProps)(FilterByOfferTypes)
