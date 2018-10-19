import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

const checkboxes = [
  {
    label: 'Tout de suite !',
    value: '0-1',
  },
  {
    label: 'Entre 1 et 5 jours',
    value: '1-5',
  },
  {
    label: 'Plus de 5 jours',
    // will the pass culture live for ever?
    // guess that 273 years are enough
    value: '5-100000',
  },
  {
    label: 'DATE PICKER TO DO',
    value: 'date-picker',
  },
]

class FilterByDates extends PureComponent {
  onChange = day => {
    const { filterActions, filterState } = this.props

    const days = decodeURI(filterState.query.jours || '')
    const isAlreadyIncluded = days.includes(day)

    // WE ADD THE DATE AT THE FIRST DAYS SEGMENTS CLICKED
    // WE REMOVE THE DATE AT THE LAST DAYS SEGMENTS CLICKED
    let callback
    if (!get(days, 'length')) {
      const date = moment(moment.now()).toISOString()
      callback = () => filterActions.change({ date })
    } else if (isAlreadyIncluded && days.split(',').length === 1) {
      callback = () => filterActions.change({ date: null })
    }
    if (isAlreadyIncluded) {
      filterActions.remove('jours', day, callback)
      return
    }

    filterActions.add('jours', day, callback)
  }

  render() {
    const { filterState, title } = this.props

    const days = decodeURI(filterState.query.jours || '')

    return (
      <div id="filter-by-dates" className="pt18">
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
          {title}
        </h2>
        {/* FIXME: le scroll sous ios est pas terrible
        du fait que le input soit cliquable */}
        <div className="pc-scroll-horizontal is-relative is-full-width pb18">
          <div className="list flex-columns pl18 pr18">
            {checkboxes.map(({ label, value }) => (
              <label
                key={value}
                className="item flex-columns items-center py5 pl7 pr22"
              >
                <span className="flex-0 field field-checkbox">
                  <input
                    type="checkbox"
                    className="input no-background"
                    checked={days.includes(value)}
                    onChange={() => this.onChange(value)}
                  />
                </span>
                <span className="fs19 flex-1" style={{ whiteSpace: 'pre' }}>
                  {label}
                </span>
              </label>
            ))}
          </div>
        </div>
        <hr className="dotted-bottom-primary" />
      </div>
    )
  }
}

FilterByDates.propTypes = {
  filterActions: PropTypes.object.isRequired,
  filterState: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
}

export default FilterByDates
