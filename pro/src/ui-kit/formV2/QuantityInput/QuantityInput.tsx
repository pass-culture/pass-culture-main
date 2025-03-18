import { useState, useRef } from 'react'
import { useFormContext } from 'react-hook-form'

import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { TextInputProps } from 'ui-kit/form/TextInput/TextInput'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

export type Quantity = string | number | ''

export type QuantityInputProps = Pick<
  TextInputProps,
  | 'name'
  | 'label'
  | 'className'
  | 'disabled'
  | 'required'
  | 'isLabelHidden'
  | 'min'
>

/**
 * The QuantityInput component is a combination of a TextInput and a BaseCheckbox to define quantities.
 * It integrates with React Hook Form for form state management and is used when an undefined quantity is meant to be interpreted as unlimited.
 * 
 * @param {QuantityInputProps} props - The props for the QuantityInput component.
 * @returns {JSX.Element} The rendered QuantityInput component.
 * 
 * @example
 * <QuantityInput
 *  {...register('quantity')}
 *  label="Quantity"
 *  required
 * />
 *  
**/
export const QuantityInput = ({
  name,
  label = 'Quantité',
  disabled,
  className,
  isLabelHidden,
  min = 0,
  required,
}: QuantityInputProps) => {
  const quantityName = name
  const quantityRef = useRef<HTMLInputElement>(null)

  const unlimitedName = `${name}.unlimited`
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const { setValue, getValues } = useFormContext()
  const initialValue = getValues(quantityName)
  const [isUnlimited, setIsUnlimited] = useState(initialValue === '')

  const onCheckboxChange = () => {
      const nextIsUnlimitedState = !isUnlimited
      setIsUnlimited(nextIsUnlimitedState)
  
      let nextFieldValue: Quantity = min
      if (nextIsUnlimitedState) {
        // If the checkbox is going to be checked,
        // we need to clear the quantity field as an empty
        // string means unlimited quantity.
        nextFieldValue = ''
      }
  
      setValue(quantityName, nextFieldValue)
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
      inputExtension={inputExtension}
    />
  )
}