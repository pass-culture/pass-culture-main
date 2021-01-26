import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'

class HiddenField extends PureComponent {
  renderField = ({ input, meta }) => {
    return (
      <Fragment>
        <input
          {...input}
          id={this.props.id}
          type="hidden"
        />
        <FormError meta={meta} />
      </Fragment>
    )
  }

  render() {
    return (
      <Field
        name={this.props.name}
        render={this.renderField}
        validate={this.props.validator}
      />
    )
  }
}

HiddenField.defaultProps = {
  id: undefined,
  validator: undefined,
}

HiddenField.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
