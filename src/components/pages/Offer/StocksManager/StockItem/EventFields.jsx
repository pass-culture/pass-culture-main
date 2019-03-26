import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'

import { DateField, HiddenField, TimeField } from 'components/layout/form'

export class EventFields extends Component {
  /*
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
  */

  render() {
    const { beginningMinDate, readOnly, stocks, tz } = this.props
    const highlightDates = (stocks || []).map(stock => stock.beginningDatetime)

    return (
      <Fragment>
        <td>
          <DateField
            highlightDates={highlightDates}
            minDate={beginningMinDate || moment()}
            name="beginningDatetime"
            readOnly={readOnly}
            required
            title="Date"
          />
        </td>
        <td>
          <TimeField
            name="beginningTime"
            patchKey="beginningDatetime"
            readOnly={readOnly}
            required
            title="Heure"
            tz={tz}
          />
        </td>
        <td>
          <HiddenField name="endDatetime" />
          <TimeField
            name="endTime"
            patchKey="endDatetime"
            readOnly={readOnly}
            required
            title="Heure de fin"
            tz={tz}
          />
        </td>
      </Fragment>
    )
  }
}

EventFields.defaultProps = {
  beginningMinDate: null,
  stocks: null,
}

EventFields.propTypes = {
  beginningMinDate: PropTypes.string,
  dispatch: PropTypes.func.isRequired,
  stocks: PropTypes.array,
}

export default EventFields
