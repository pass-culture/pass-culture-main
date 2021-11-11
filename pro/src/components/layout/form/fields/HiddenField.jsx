/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt deprecated "Gaël: deprecated usage of react-final-form"
* @debt standard "Gaël: migration from classes components to function components"
*/

import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'

import FieldErrors from '../FieldErrors'

const noOperation = () => {}

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class HiddenField extends PureComponent {
  renderField = ({ input, meta }) => (
    <div>
      <input
        {...input}
        type="hidden"
      />
      <FieldErrors meta={meta} />
    </div>
  )

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
  validator: noOperation,
}

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
