import { useField } from 'formik'

import { Checkbox, CheckboxVariant } from 'design-system/Checkbox/Checkbox'
import { CheckboxAssetVariant } from 'design-system/Checkbox/CheckboxAsset/CheckboxAsset'

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
      asset={
        icon ? { variant: CheckboxAssetVariant.ICON, src: icon } : undefined
      }
      hasError={hasError}
      label={label}
      onChange={onCustomChange}
      disabled={disabled}
      variant={CheckboxVariant.DETAILED}
      display="fill"
      collapsed={collapsed}
      name={name}
      checked={Boolean(field.checked)}
    />
  )
}
