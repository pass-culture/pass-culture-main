import { useEffect, useState, useRef } from 'react'

import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { TextInput, TextInputProps } from 'ui-kit/formV2/TextInput/TextInput'

/**
 * Props for the QuantityInput component.
 *
 * @extends Pick<TextInputProps, 'disabled' | 'className' | 'classNameFooter' | 'isLabelHidden' | 'required'>
 */
export type QuantityInputProps = Pick<
  TextInputProps,
  'disabled' | 'className' | 'isLabelHidden' | 'required'
> & {
  /**
   * A label for the input, also used as the aria-label for the group.
   */
  label?: string
  /**
   * The name of the input, mind what's being used in the formik form.
   */
  name?: string
  /**
   * A callback when the quantity changes.
   * If not provided, the value will be set in the formik form, otherwise, setFieldValue must be called manually.
   * This is to support custom logic when the quantity changes.
   */
  onChange?: (quantity: string) => void
  /**
   * The minimum value allowed for the quantity. Make sure it matches formik validation schema.
   */
  min?: string
}

/**
 * The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
 * It integrates with Formik for form state management and is used when an undefined quantity is meant to be interpreted as unlimited.
 *
 * @param {QuantityInputProps} props - The props for the QuantityInput component.
 * @returns {JSX.Element} The rendered QuantityInput component.
 *
 * @example
 * <QuantityInput
 *   label="Quantity"
 *   name="quantity"
 *   min={0}
 *   onChange={(value) => console.log(value)}
 * />
 *
 * @accessibility
 * - **Labels**: Always provide a meaningful label using the `label` prop for screen readers. This helps users understand the purpose of the input.
 * - **Keyboard Accessibility**: Users can navigate the input and checkbox using the keyboard, ensuring accessibility for all users.
 * - **ARIA Attributes**: The component uses an `aria-label` to group the input and checkbox for context. Make sure the label is descriptive and helpful.
 */
export const QuantityInput = ({
  label = 'Quantité',
  name = 'quantity',
  onChange,
  disabled,
  className,
  isLabelHidden,
  required,
  min = '0',
}: QuantityInputProps) => {
  const quantityName = name
  const quantityRef = useRef<HTMLInputElement>(null)

  const unlimitedName = `${name}.unlimited`
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const isEmptyValue =
    quantityRef.current?.value === '' ||
    quantityRef.current?.value === undefined
  const [isUnlimited, setIsUnlimited] = useState(isEmptyValue)

  useEffect(() => {
    // Move focus to the quantity input if unlimited is unchecked.
    const focusedElement = document.activeElement as HTMLElement
    const isUnlimitedCheckboxFocused = focusedElement === unlimitedRef.current
    if (!isUnlimited && isUnlimitedCheckboxFocused) {
      quantityRef.current?.focus()
    }
  }, [isUnlimited])

  const onQuantityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextValue = event.target.value || ''
    setIsUnlimited(nextValue === '')
    onChange?.(nextValue)
  }

  const onCheckboxChange = () => {
    const nextIsUnlimitedState = !isUnlimited
    setIsUnlimited(nextIsUnlimitedState)

    let nextFieldValue = min
    if (nextIsUnlimitedState) {
      // If the checkbox is going to be checked,
      // we need to clear the quantity field as an empty
      // string means unlimited quantity.
      nextFieldValue = ''
    }

    if (onChange) {
      onChange(nextFieldValue)
    } else {
      if (quantityRef.current) {
        quantityRef.current.value = nextFieldValue
      }
    }
  }

  const inputExtension = (
    <BaseCheckbox
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
      name={quantityName}
      label={label}
      required={required}
      disabled={disabled}
      type="number"
      hasDecimal={false}
      className={className}
      min={min}
      max={1_000_000}
      isLabelHidden={isLabelHidden}
      step={1}
      InputExtension={inputExtension}
      onChange={onQuantityChange}
    />
  )
}
