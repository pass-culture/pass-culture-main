import { useField } from 'formik'

import {
  BaseCheckbox,
  CheckboxVariant,
} from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

interface CheckboxGroupItemProps {
  setGroupTouched(): void
  name: string
  label: string
  description?: string
  icon?: string
  hasError?: boolean
  disabled?: boolean
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  ariaDescribedBy?: string
  variant?: CheckboxVariant
  childrenOnChecked?: JSX.Element
}

export const CheckboxGroupItem = ({
  setGroupTouched,
  label,
  name,
  hasError,
  icon,
  disabled,
  onChange,
  ariaDescribedBy,
  variant,
  childrenOnChecked,
}: CheckboxGroupItemProps): JSX.Element => {
  const [field] = useField({ name, type: 'checkbox' })

  const onCustomChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setGroupTouched()
    field.onChange(event)
    if (onChange) {
      onChange(event)
    }
  }

  return (
    <BaseCheckbox
      {...field}
      icon={icon}
      hasError={hasError}
      label={label}
      onChange={onCustomChange}
      disabled={disabled}
      ariaDescribedBy={ariaDescribedBy}
      variant={variant}
      childrenOnChecked={childrenOnChecked}
    />
  )
}
