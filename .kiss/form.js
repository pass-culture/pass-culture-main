import React from 'react'
import moment from 'moment'
import get from 'lodash.get'
import PropTypes from 'prop-types'

import withForm from './withForm'
import { TimeField, CalendarField } from './fields'

class MyForm extends React.PureComponent {
  render() {
    const { item } = this.props
    return (
      <React.Fragment />
    )
  }
}

MyForm.defaultProps = {
  item: null,
}

MyForm.propTypes = {
  item: PropTypes.object,
}

const BookingForm = withForm(MyForm, null, null)
export default BookingForm
