import React from 'react'
import PropTypes from 'prop-types'
import { Form, Select } from 'antd'
import { Field } from 'react-final-form'

import { renderLabel } from '../utils'

const filterOption = (input, option) => {
  const child = option.props.children
  return child.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

class SelectField extends React.PureComponent {
  constructor(props) {
    super(props)
    this.popupContainer = null
  }

  setContainerRef = ref => {
    this.popupContainer = ref
  }

  renderSelect = (placeholder, canSearch, moreProps, provider) => {
    return ({input}) => (
      <Select
        filterOption={filterOption}
        getPopupContainer={this.getPopupContainer()}
        onChange={input.onChange}
        optionFilterProp="children"
        placeholder={placeholder}
        showSearch={canSearch}
        size="large"
        value={input.value || undefined}
        {...moreProps}
      >
        {provider &&
        provider.map(obj => (
          <Select.Option
            key={obj.id}
            value={obj.id}
          >
            {obj.label}
          </Select.Option>
        ))}
      </Select>
    )
  }

  getPopupContainer = () => {
    return () => this.popupContainer
  }

  render() {
    const {
      label,
      help,
      id,
      name,
      disabled,
      provider,
      className,
      canSearch,
      placeholder,
      readOnly,
      ...rest
    } = this.props
    const isDisabled = readOnly || disabled || !provider.length || provider.length === 1
    const moreProps = {disabled: isDisabled}

    if (id) moreProps.id = id

    return (
      <Form.Item
        {...rest}
        className={`ant-select-custom ${className}`}
        label={(label && renderLabel(label, help)) || null}
      >
        <Field
          name={name}
          render={this.renderSelect(placeholder, canSearch, moreProps, provider)}
        />
        <div
          className="select-field-popup-container is-relative"
          ref={this.setContainerRef}
        />
      </Form.Item>
    )
  }
}

SelectField.defaultProps = {
  canSearch: false,
  className: '',
  disabled: false,
  help: null,
  id: null,
  label: null,
  placeholder: null,
  readOnly: false,
}

SelectField.propTypes = {
  canSearch: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  help: PropTypes.string,
  id: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  provider: PropTypes.shape().isRequired,
  readOnly: PropTypes.bool,
}

export default SelectField
