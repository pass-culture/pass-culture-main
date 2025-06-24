import classNames from 'classnames'
import { useEffect, useState, useRef } from 'react'

import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { TextInput, TextInputProps } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './QuantityInput.module.scss'

export type QuantityInputProps = Pick<
  TextInputProps,
  | 'disabled'
  | 'className'
  | 'required'
  | 'asterisk'
  | 'smallLabel'
  | 'className'
> & {
  /**
   * A label for the text input.
   */
  label: string
  /**
   * The name of the input, mind what's being used in the form.
   */
  name?: string
  /**
   * A callback when the quantity changes.
   */
  onChange?: React.InputHTMLAttributes<HTMLInputElement>['onChange']
  /**
   * A callback when the quantity text input is blurred.
   */
  onBlur?: React.InputHTMLAttributes<HTMLInputElement>['onBlur']
  /**
   * The quantity value. Should be `undefined` if the quantity is unlimited.
   */
  value?: number
  /**
   * The minimum value allowed for the quantity. Make sure it matches validation schema.
   */
  minimum?: number
  /**
   * The maximum value allowed for the quantity. Make sure it matches validation schema.
   */
  maximum?: number
  error?: string
}

/**
 * The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
 * An undefined quantity is meant to be interpreted as unlimited.
 *
 * @example
 * <QuantityInput
 *   label="Quantity"
 *   name="quantity"
 *   min={0}
 *   onChange={(value) => console.log(value)}
 * />
 */
export const QuantityInput = ({
  label = 'Quantité',
  name = 'quantity',
  onChange,
  onBlur,
  disabled,
  className,
  required,
  asterisk,
  minimum = 0,
  maximum = 1_000_000,
  value,
  error,
}: QuantityInputProps) => {
  const quantityName = name
  const quantityRef = useRef<HTMLInputElement>(null)

  const unlimitedName = `${name}.unlimited`
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const isEmptyValue = value !== 0 && !value
  const [isUnlimited, setIsUnlimited] = useState(isEmptyValue)

  useEffect(() => {
    // Move focus to the quantity input if unlimited is unchecked.
    const focusedElement = document.activeElement as HTMLElement
    const isUnlimitedCheckboxFocused = focusedElement === unlimitedRef.current
    if (!isUnlimited && isUnlimitedCheckboxFocused) {
      quantityRef.current?.focus()
    }
  }, [isUnlimited])

  useEffect(() => {
    if (isUnlimited !== isEmptyValue) {
      setIsUnlimited(isEmptyValue)
    }
  }, [isEmptyValue])

  const onQuantityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(event)

    setIsUnlimited(event.target.value === '')
  }

  const onCheckboxChange = () => {
    let nextFieldValue = `${minimum}`
    if (!isUnlimited) {
      // If the checkbox is going to be checked,
      // we need to clear the quantity field as an empty
      // string means unlimited quantity.
      nextFieldValue = ''
    }

    onChange?.({
      target: { value: nextFieldValue },
    } as React.ChangeEvent<HTMLInputElement>)

    if (quantityRef.current) {
      quantityRef.current.value = nextFieldValue
    }

    setIsUnlimited((unlimited) => !unlimited)
  }

  const inputExtension = (
    <Checkbox
      ref={unlimitedRef}
      label="Illimité"
      name={unlimitedName}
      onChange={onCheckboxChange}
      checked={isUnlimited}
      disabled={disabled}
    />
  )

  return (
    <TextInput
      ref={quantityRef}
      className={classNames(styles['quantity-row'], className)}
      name={quantityName}
      label={label}
      required={required}
      asterisk={asterisk}
      disabled={disabled}
      type="number"
      hasDecimal={false}
      min={minimum}
      max={maximum}
      step={1}
      InputExtension={inputExtension}
      onChange={onQuantityChange}
      onBlur={onBlur}
      value={isUnlimited ? '' : value === 0 ? '0' : value || ''}
      error={error}
    />
  )
}
