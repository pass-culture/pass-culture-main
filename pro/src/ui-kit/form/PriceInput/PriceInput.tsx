import { useField, useFormikContext } from 'formik'
import { useState, useEffect, useRef } from 'react'

import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { TextInput, TextInputProps } from 'ui-kit/form/TextInput/TextInput'

type Price = number | ''

/**
 * Props for the PriceInput component.
 *
 * @extends Pick<TextInputProps, 'name' | 'max' | 'rightIcon' | 'disabled' | 'smallLabel' | 'className'>
 */
export type PriceInputProps = Pick<
  TextInputProps,
  'name' | 'max' | 'rightIcon' | 'disabled' | 'smallLabel' | 'className'
> & {
  /**
   * A label for the input,
   * also used as the aria-label for the group.
   */
  label: string
  /**
   * A flag to show the "Gratuit" checkbox.
   */
  showFreeCheckbox?: boolean
}

/**
 * The PriceInput component is a combination of a TextInput and a Checkbox to define prices.
 * It integrates with Formik for form state management and is used when an null price is meant to be interpreted as free.
 *
 * ---
 *
 * @param {PriceInputProps} props - The props for the PriceInput component.
 * @returns {JSX.Element} The rendered PriceInput component.
 *
 * @example
 * <PriceInput
 *  label="Price"
 *  name="price"
 *  max={100}
 *  rightIcon={strokeEuroIcon}
 * />
 *
 * @accessibility
 * - **Labels**: Always provide a meaningful label using the `label` prop.
 */
export const PriceInput = ({
  className,
  name,
  label,
  max,
  rightIcon,
  disabled,
  smallLabel,
  showFreeCheckbox,
}: PriceInputProps): JSX.Element => {
  const priceName = name
  const priceRef = useRef<HTMLInputElement>(null)

  const freeName = `${name}.free`
  const freeRef = useRef<HTMLInputElement>(null)

  const [field] = useField(priceName)
  const { setFieldValue } = useFormikContext()
  const [isFree, setIsFree] = useState(field.value === 0)

  useEffect(() => {
    showFreeCheckbox && setIsFree(field.value === 0)
  }, [showFreeCheckbox, field.value])

  useEffect(() => {
    // Move focus to the price input if free is unchecked.
    const focusedElement = document.activeElement as HTMLElement
    const isFreeCheckboxFocused = focusedElement === freeRef.current
    if (!isFree && isFreeCheckboxFocused) {
      priceRef.current?.focus()
    }
  }, [isFree])

  const onCheckboxChange = async () => {
    const nextIsFreeState = !isFree

    let nextFieldValue: Price = ''
    if (nextIsFreeState) {
      // If the checkbox is going to be checked,
      // we need to clear the quantity field as an empty
      // string means unlimited quantity.
      nextFieldValue = 0
    }

    await setFieldValue(priceName, nextFieldValue)
  }

  const inputExtension = (
    <BaseCheckbox
      ref={freeRef}
      label="Gratuit"
      checked={isFree}
      name={freeName}
      onChange={onCheckboxChange}
      disabled={disabled}
    />
  )

  return (
    <TextInput
      refForInput={priceRef}
      className={className}
      smallLabel={smallLabel}
      name={priceName}
      label={label}
      type="number"
      step="0.01"
      min={0}
      max={max}
      rightIcon={rightIcon}
      disabled={disabled}
      {...(showFreeCheckbox ? { InputExtension: inputExtension } : {})}
    />
  )
}
