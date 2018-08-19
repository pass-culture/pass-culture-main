import React from 'react'
import PropTypes from 'prop-types'
import { Form, Select } from 'antd'
import { Field } from 'react-final-form'

import renderLabel from '../renderLabel'

const filterOption = (input, option) => {
  const child = option.props.children
  return child.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

export class SelectField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.popupContainer = null
  }

  setContainerRef = ref => {
    this.popupContainer = ref
  }

  render() {
    const {
      label,
      help,
      name,
      disabled,
      provider,
      canSearch,
      placeholder,
      ...rest
    } = this.props
    return (
      <Form.Item
        {...rest}
        className="select-field"
        label={renderLabel(label, help)}
      >
        <Field
          name={name}
          render={({ input }) => (
            <Select
              size="large"
              showSearch={canSearch}
              onChange={input.onChange}
              placeholder={placeholder}
              optionFilterProp="children"
              filterOption={filterOption}
              value={input.value || undefined}
              getPopupContainer={() => this.popupContainer}
              disabled={disabled || !provider.length || provider.length === 1}
            >
              {provider &&
                provider.map(obj => (
                  <Select.Option key={obj.id} value={obj.id}>
                    {obj.label}
                  </Select.Option>
                ))}
            </Select>
          )}
        />
        <div
          ref={this.setContainerRef}
          className="select-field-popup-container is-relative"
        />
      </Form.Item>
    )
  }
}

SelectField.defaultProps = {
  canSearch: false,
  disabled: null,
  help: null,
  label: null,
  placeholder: null,
}

SelectField.propTypes = {
  canSearch: PropTypes.bool,
  disabled: PropTypes.string,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  provider: PropTypes.array.isRequired,
}

export default SelectField
