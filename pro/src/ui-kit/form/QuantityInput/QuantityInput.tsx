import { useField, useFormikContext } from 'formik'
import { useEffect, useState, useRef } from 'react'

import { Checkbox } from 'design-system/Checkbox/Checkbox'
import { TextInput, TextInputProps } from 'ui-kit/form/TextInput/TextInput'

type Quantity = number | ''

/**
 * Props for the QuantityInput component.
 *
 * @extends Pick<TextInputProps, 'disabled' | 'className' | 'classNameFooter' | 'isLabelHidden' | 'smallLabel' | 'isOptional'>
 */
export type QuantityInputProps = Pick<
  TextInputProps,
  | 'disabled'
  | 'className'
  | 'classNameFooter'
  | 'isLabelHidden'
  | 'smallLabel'
  | 'isOptional'
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
  onChange?: (quantity: Quantity) => void
  /**
   * The minimum value allowed for the quantity. Make sure it matches formik validation schema.
   */
  min?: Quantity
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
  classNameFooter,
  isLabelHidden,
  smallLabel,
  isOptional,
  min = 0,
}: QuantityInputProps) => {
  const quantityName = name
  const quantityRef = useRef<HTMLInputElement>(null)

  const unlimitedName = `${name}.unlimited`
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const [field] = useField(quantityName)
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
      await setFieldValue(quantityName, nextFieldValue)
    }
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
      focusRef={quantityRef}
      smallLabel={smallLabel}
      name={quantityName}
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
      step={1}
      InputExtension={inputExtension}
      {...(onChange && { onChange: onQuantityChange })}
    />
  )
}
