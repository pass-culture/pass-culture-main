/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt deprecated "Gaël: deprecated usage of react-final-form"
* @debt standard "Gaël: migration from classes components to function components"
*/

import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class CheckboxField extends PureComponent {
  renderLabelAlignedField = ({ input }) => {
    const { checked, id, label } = this.props

    return (
      <div className="field is-label-aligned">
        <div className="field-label" />
        <div className="field-control">
          <input
            {...input}
            className="field-checkbox"
            defaultChecked={checked}
            id={id}
            type="checkbox"
          />
          {label && (
            <label htmlFor={id}>
              {label}
            </label>
          )}
        </div>
      </div>
    )
  }

  renderField = ({ input }) => {
    const { checked, id, label, labelAligned } = this.props

    if (labelAligned) {
      return this.renderLabelAlignedField({ input })
    }

    return (
      <div>
        <input
          {...input}
          defaultChecked={checked}
          id={id}
          type="checkbox"
        />
        {label && (
          <label htmlFor={id}>
            {label}
          </label>
        )}
      </div>
    )
  }

  render() {
    const { name } = this.props

    return (
      <Field
        name={name}
        render={this.renderField}
      />
    )
  }
}

CheckboxField.defaultProps = {
  checked: true,
  label: '',
  labelAligned: false,
}

CheckboxField.propTypes = {
  checked: PropTypes.bool,
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelAligned: PropTypes.bool,
  name: PropTypes.string.isRequired,
}

export default CheckboxField
