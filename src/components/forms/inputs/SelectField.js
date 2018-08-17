import React from 'react'
import PropTypes from 'prop-types'
import { Form, Select } from 'antd'
import { Field } from 'react-final-form'

import renderLabel from '../renderLabel'

const filterOption = (input, option) => {
  const child = option.props.children
  return child.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

export const SelectField = ({
  label,
  help,
  name,
  provider,
  canSearch,
  placeholder,
  ...rest
}) => (
  <Form.Item
    {...rest}
    className="select-field"
    label={renderLabel(label, help)}
  >
    <Field
      name={name}
      render={({ input }) => (
        <Select
          showSearch={canSearch}
          onChange={input.onChange}
          placeholder={placeholder}
          optionFilterProp="children"
          disabled={!provider.length}
          filterOption={filterOption}
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
  </Form.Item>
)

SelectField.defaultProps = {
  canSearch: false,
  help: null,
  label: null,
  placeholder: null,
}

SelectField.propTypes = {
  canSearch: PropTypes.bool,
  help: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  provider: PropTypes.array.isRequired,
}

export default SelectField
