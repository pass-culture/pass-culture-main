import React from 'react'
import PropTypes from 'prop-types'

import withForm from '../forms/withForm'

class MyForm extends React.PureComponent {
  render() {
    const { item } = this.props
    return <React.Fragment />
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
