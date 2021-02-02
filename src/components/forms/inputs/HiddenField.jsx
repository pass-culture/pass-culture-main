import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'

class HiddenField extends PureComponent {
  renderField = ({ input, meta }) => {
    const { id } = this.props

    return (
      <Fragment>
        <input
          {...input}
          id={id}
          type="hidden"
        />
        <FormError meta={meta} />
      </Fragment>
    )
  }

  render() {
    const { name, validator } = this.props

    return (
      <Field
        name={name}
        render={this.renderField}
        validate={validator}
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
