import { Select } from 'antd'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Field } from 'react-final-form'

const Option = Select.Option

const filterOption = (input, option) => {
  const child = option.props.children
  return child.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

class SelectField extends PureComponent {
  constructor(props) {
    super(props)
    this.popupContainer = null
  }

  getPopupContainer = () => {
    return () => this.popupContainer
  }

  setContainerRef = ref => {
    this.popupContainer = ref
  }

  /*
  renderSuffixIcon(prefixCls: string) {
    const { loading, suffixIcon } = this.props;
    if (suffixIcon) {
      return React.isValidElement<{ className?: string }>(suffixIcon)
        ? React.cloneElement(suffixIcon, {
            className: classnames(suffixIcon.props.className, `${prefixCls}-arrow-icon`),
          })
        : suffixIcon;
    }
    if (loading) {
      return <Icon type="loading" />;
    }
    return <Icon type="down" className={`${prefixCls}-arrow-icon`} />;
  }
  */
  renderSelect = ({ input }) => {
    const { canSearch, disabled, id, options, placeholder, readOnly, ...rest } = this.props
    const hasNoOption = !options.length
    const hasOneOption = options.length === 1
    const isDisabled = readOnly || disabled || hasNoOption || hasOneOption

    const moreProps = { ...rest }
    if (id) moreProps.id = id

    const { onChange, value } = input

    return (
      <Select
        disabled={isDisabled}
        filterOption={filterOption}
        getPopupContainer={this.getPopupContainer()}
        onChange={onChange}
        optionFilterProp="children"
        placeholder={placeholder}
        showSearch={canSearch}
        size="large"
        value={value || undefined}
        {...moreProps}
      >
        {options &&
          options.map(option => (
            <Option
              key={option.id}
              value={option.id}
            >
              {option.label}
            </Option>
          ))}
      </Select>
    )
  }

  render() {
    const { name, className } = this.props
    return (
      <div className={`ant-select-custom ${className}`}>
        <Field
          name={name}
          render={this.renderSelect}
        />
        <div
          className="select-field-popup-container is-relative"
          ref={this.setContainerRef}
        />
      </div>
    )
  }
}

SelectField.defaultProps = {
  canSearch: false,
  className: '',
  disabled: false,
  id: null,
  placeholder: null,
  readOnly: false,
}

SelectField.propTypes = {
  canSearch: PropTypes.bool,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
}

export default SelectField
