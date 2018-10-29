import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypes'
import SearchPicture from './SearchPicture'

class FilterByOfferTypes extends PureComponent {
  onChange = typeSublabel => {
    const { filterActions, filterState } = this.props

    const typesValue = decodeURI(filterState.query.categories || '')

    const isAlreadyIncluded = typesValue.includes(typeSublabel)

    if (isAlreadyIncluded) {
      filterActions.remove('categories', typeSublabel)
      return
    }

    filterActions.add('categories', typeSublabel)
  }

  render() {
    const { filterState, typeSublabels, title } = this.props

    const typesValue = decodeURI(filterState.query.categories || '')

    return (
      <div id="filter-by-offer-types" className="pt18">
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
          {title}
        </h2>
        <div className="pc-scroll-horizontal is-relative is-full-width">
          <div className="pc-list flex-columns pl18 pr18">
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
                  {ischecked && (
                    <input
                      type="checkbox"
                      id="offer-type-picture-checked"
                      defaultChecked={ischecked}
                    />
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

function mapStateToProps(state) {
  return {
    typeSublabels: selectTypeSublabels(state),
  }
}

export default connect(mapStateToProps)(FilterByOfferTypes)
