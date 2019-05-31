import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypes'
import SearchPicture from './SearchPicture'

class FilterByOfferTypes extends PureComponent {
  onChangeType = typeSublabel => () => {
    const { filterActions, filterState } = this.props

    const typesValue = decodeURI(filterState.params.categories || '')

    const isAlreadyIncluded = typesValue.includes(typeSublabel)

    if (isAlreadyIncluded) {
      filterActions.remove('categories', typeSublabel)
      return
    }

    filterActions.add('categories', typeSublabel)
  }

  render() {
    const { filterState, typeSublabels, title } = this.props
    const typesValue = decodeURI(filterState.params.categories || '')

    return (
      <div id="filter-by-offer-types" className="pt18">
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
          {title}
        </h2>
        <div className="pc-scroll-horizontal is-relative">
          <div className="pc-list flex-columns pt7">
            {typeSublabels.map((typeSublabel, index) => {
              const ischecked = typesValue.includes(typeSublabel)
              const className = ischecked ? 'checked' : ''
              const inputName = `search-image-checkbox-${index}`

              return (
                <label
                  htmlFor={inputName}
                  key={typeSublabel}
                  className={`item p3 is-relative ${className}`}
                >
                  <SearchPicture searchType={typeSublabel} />
                  <input
                    id={inputName}
                    checked={ischecked}
                    className="is-hidden"
                    onChange={this.onChangeType(typeSublabel)}
                    value={typeSublabel}
                    type="checkbox"
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
