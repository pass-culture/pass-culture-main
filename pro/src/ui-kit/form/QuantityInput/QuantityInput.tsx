import classNames from 'classnames'
import { useField, useFormikContext } from 'formik'
import { useEffect, useState, useRef } from 'react'

import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { TextInput, TextInputProps } from 'ui-kit/form/TextInput/TextInput'

import styles from './QuantityInput.module.scss'

export type Quantity = number | ''
export type QuantityInputProps = Pick<
  TextInputProps,
  | 'disabled'
  | 'className'
  | 'classNameFooter'
  | 'isLabelHidden'
  | 'smallLabel'
  | 'hideFooter'
  | 'isOptional'
> & {
  /**
   * A label for the input,
   * also used as the aria-label for the group.
   */
  label?: string
  /**
   * The name of the input,
   * mind what's being used in the formik form.
   */
  name?: string
  /**
   * A callback when the quantity changes.
   * If not provided, the value will be set in the formik form,
   * otherwise, setFieldValue must be called manually.
   * This is to support custom logic when the quantity changes.
   */
  onChange?: (quantity: Quantity) => void
  /**
   * The minimum value allowed for the quantity.
   * Make sure it matches formik validation schema.
   */
  min?: Quantity
}

export const QuantityInput = ({
  label = 'Quantité',
  name = 'quantity',
  onChange,
  disabled,
  className,
  classNameFooter,
  isLabelHidden,
  smallLabel,
  hideFooter,
  isOptional,
  min = 0,
}: QuantityInputProps) => {
  const quantityRef = useRef<HTMLInputElement>(null)
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const [field] = useField(name)
  const { setFieldValue } = useFormikContext()
  const [isUnlimited, setIsUnlimited] = useState(field.value === '')

  useEffect(() => {
    setIsUnlimited(field.value === '')
  }, [field.value])

  useEffect(() => {
    // Move focus to the quantity input if unlimited is unchecked.
    const focusedElement = document.activeElement as HTMLElement
    const isUnlimitedCheckboxFocused = focusedElement === unlimitedRef.current
    if (!isUnlimited && isUnlimitedCheckboxFocused) {
      quantityRef.current?.focus()
    }
  }, [isUnlimited])

  const onQuantityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextValue = event.target.value ? parseInt(event.target.value) : ''
    onChange?.(nextValue)
  }

  const onCheckboxChange = async () => {
    const nextIsUnlimitedState = !isUnlimited
    setIsUnlimited(nextIsUnlimitedState)

    let nextFieldValue: Quantity = min
    if (nextIsUnlimitedState) {
      // If the checkbox is going to be checked,
      // we need to clear the quantity field as an empty
      // string means unlimited quantity.
      nextFieldValue = ''
    }

    if (onChange) {
      onChange(nextFieldValue)
    } else {
      await setFieldValue(name, nextFieldValue)
    }
  }

  return (
    <div className={styles['quantity-input']} role="group" aria-label={label}>
      <TextInput
        refForInput={quantityRef}
        smallLabel={smallLabel}
        name={name}
        label={label}
        isOptional={isOptional}
        disabled={disabled}
        type="number"
        hasDecimal={false}
        className={className}
        classNameFooter={classNameFooter}
        min={min}
        max={1_000_000}
        isLabelHidden={isLabelHidden}
        hideFooter={hideFooter}
        step={1}
        {...(onChange && { onChange: onQuantityChange })}
      />
      <Checkbox
        refForInput={unlimitedRef}
        hideFooter
        label="Illimité"
        name="unlimited"
        onChange={onCheckboxChange}
        checked={isUnlimited}
        className={classNames(styles['quantity-input-checkbox'], {
          [styles['quantity-input-checkbox-for-small-label']]: smallLabel,
          [styles['quantity-input-checkbox-for-hidden-label']]: isLabelHidden,
        })}
        disabled={disabled}
      />
    </div>
  )
}
