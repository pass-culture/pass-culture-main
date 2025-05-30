import { useField } from 'formik'

import { Checkbox, CheckboxProps } from 'design-system/Checkbox/Checkbox'

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
  variant?: CheckboxProps['variant']
  collapsed?: JSX.Element
}

export const CheckboxGroupItem = ({
  setGroupTouched,
  label,
  name,
  hasError,
  icon,
  disabled,
  onChange,
  collapsed,
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
    <Checkbox
      asset={icon ? { variant: 'icon', src: icon } : undefined}
      hasError={hasError}
      label={label}
      onChange={onCustomChange}
      disabled={disabled}
      variant="detailed"
      display="fill"
      collapsed={collapsed}
      name={name}
      checked={Boolean(field.checked)}
    />
  )
}
