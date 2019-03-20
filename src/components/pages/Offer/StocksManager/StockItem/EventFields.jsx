import { Field, mergeForm, recursiveMap } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'

import { getDatetimeOneDayAfter } from './utils'

export class EventFields extends Component {
  componentDidUpdate(prevProps) {
    this.handleCrossingEndDatetime()
  }

  handleCrossingEndDatetime = () => {
    const {
      dispatch,
      formBeginningDatetime,
      formEndDatetime,
      stockFormKey,
    } = this.props

    if (formEndDatetime >= formBeginningDatetime) {
      return
    }

    const endDatetime = getDatetimeOneDayAfter(formBeginningDatetime)

    dispatch(mergeForm(`stock${stockFormKey}`, { endDatetime }))
  }

  render() {
    const {
      beginningDatetime,
      isReadOnly,
      parseFormChild,
      stocks,
      tz,
    } = this.props
    const highlightedDates = (stocks || []).map(
      stock => stock.beginningDatetime
    )

    const children = (
      <Fragment>
        <td>
          <Field
            debug
            highlightedDates={highlightedDates}
            minDate="today"
            name="beginningDate"
            patchKey="beginningDatetime"
            readOnly={isReadOnly}
            required
            title="Date"
            type="date"
            tz={tz}
          />
        </td>
        <td>
          <Field
            name="beginningTime"
            patchKey="beginningDatetime"
            readOnly={isReadOnly}
            required
            title="Heure"
            type="time"
            tz={tz}
          />
        </td>
        <td>
          <Field minDate={beginningDatetime} name="endDatetime" type="hidden" />
          <Field
            name="endTime"
            patchKey="endDatetime"
            readOnly={isReadOnly}
            required
            title="Heure de fin"
            type="time"
            tz={tz}
          />
        </td>
      </Fragment>
    )
    return recursiveMap(children, parseFormChild)
  }
}

EventFields.defaultProps = {
  formBeginningDatetime: null,
  formBookingLimitDatetime: null,
  formEndDatetime: null,
  parseFormChild: c => c,
  stocks: null,
}

EventFields.propTypes = {
  dispatch: PropTypes.func.isRequired,
  formBeginningDatetime: PropTypes.string,
  formBookingLimitDatetime: PropTypes.string,
  formEndDatetime: PropTypes.string,
  parseFormChild: PropTypes.func,
  stocks: PropTypes.array,
}

export default EventFields
EventFields.isParsedByForm = true
