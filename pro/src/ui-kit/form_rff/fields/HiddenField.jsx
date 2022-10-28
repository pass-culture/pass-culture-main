import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'

import FieldErrors from '../FieldErrors'
/*eslint no-undef: 0*/

const noOperation = () => {}

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class HiddenField extends PureComponent {
  renderField = ({ input, meta }) => (
    <div>
      <input {...input} type="hidden" />
      <FieldErrors meta={meta} />
    </div>
  )

  render() {
    const { name, validator } = this.props

    return <Field name={name} render={this.renderField} validate={validator} />
  }
}

HiddenField.defaultProps = {
  validator: noOperation,
}

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
