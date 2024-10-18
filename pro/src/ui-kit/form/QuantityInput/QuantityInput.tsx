import { useField, useFormikContext } from 'formik'
import { useEffect, useState, useRef } from 'react'

import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { TextInput, TextInputProps } from 'ui-kit/form/TextInput/TextInput'

import styles from './QuantityInput.module.scss'

type QuantityInputProps = Omit<
  TextInputProps,
  'label' | 'name' | 'onChange'
> & {
  label?: string
  name?: string
  onChange?: (quantity: string) => void
}

export const QuantityInput = ({
  label = 'Quantité',
  name = 'quantity',
  onChange,
  disabled,
  className,
  classNameFooter,
  isLabelHidden,
}: QuantityInputProps) => {
  const quantityRef = useRef<HTMLInputElement>(null)
  const unlimitedRef = useRef<HTMLInputElement>(null)

  const [field] = useField(name)
  const { setFieldValue } = useFormikContext()
  const [isUnlimited, setIsUnlimited] = useState(!field.value)

  useEffect(() => {
    setIsUnlimited(!field.value)
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
    const newQuantity = event.target.value
    onChange?.(newQuantity)
  }

  const onCheckboxChange = async () => {
    const nextIsUnlimitedState = !isUnlimited
    setIsUnlimited(nextIsUnlimitedState)

    let nextFieldValue
    if (nextIsUnlimitedState) {
      // If the checkbox is going to be checked,
      // we need to clear the quantity field as an empty
      // string means unlimited quantity.
      nextFieldValue = ''
    }

    if (typeof nextFieldValue === 'string') {
      if (onChange) {
        onChange(nextFieldValue)
      } else {
        await setFieldValue(name, nextFieldValue)
      }
    }
  }

  return (
    <div className={styles['quantity-input']} role="group" aria-label={label}>
      <TextInput
        refForInput={quantityRef}
        smallLabel
        name={name}
        label={label}
        isOptional
        disabled={disabled}
        type="number"
        hasDecimal={false}
        onChange={onQuantityChange}
        className={className}
        classNameFooter={classNameFooter}
        min={1}
        max={1_000_000}
        isLabelHidden={isLabelHidden}
      />
      <Checkbox
        refForInput={unlimitedRef}
        hideFooter
        label="Illimité"
        name="unlimited"
        onChange={onCheckboxChange}
        checked={isUnlimited}
        className={styles['quantity-input-checkbox']}
      />
    </div>
  )
}
