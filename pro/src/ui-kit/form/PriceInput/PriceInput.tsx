import React, {
  ChangeEvent,
  ForwardedRef,
  useEffect,
  useRef,
  useState,
} from 'react'

import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { TextInput, TextInputProps } from '@/ui-kit/form/TextInput/TextInput'

import styles from './PriceInput.module.scss'

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
  hideAsterisk?: boolean
  /**
   * A custom error message to be displayed.
   * If this prop is provided, the error message will be displayed and the field will be marked as errored
   */
  error?: string
  updatePriceValue: (value: string) => void
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
export const PriceInput = React.forwardRef(
  (
    {
      className,
      name,
      label,
      max,
      rightIcon,
      disabled,
      smallLabel,
      showFreeCheckbox,
      hideAsterisk = false,
      error,
      updatePriceValue,
    }: PriceInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const priceRef = useRef<HTMLInputElement>(null)

    const freeName = `${name}.free`
    const freeRef = useRef<HTMLInputElement>(null)

    const [isFree, setIsFree] = useState(false)

    useEffect(() => {
      // Move focus to the price input if free is unchecked.
      const focusedElement = document.activeElement as HTMLElement
      const isFreeCheckboxFocused = focusedElement === freeRef.current
      if (!isFree && isFreeCheckboxFocused) {
        priceRef.current?.focus()
      }
    }, [isFree])

    useEffect(() => {
      if (freeRef.current && priceRef.current?.value === '0') {
        setIsFree(true)
      }
    }, [priceRef.current?.value, freeRef.current?.value])

    const onTextInputChange = (e: ChangeEvent<HTMLInputElement>) => {
      updatePriceValue(e.target.value)
      showFreeCheckbox && setIsFree(e.target.value === '0')
    }
    const onCheckboxChange = () => {
      const nextIsFreeState = !isFree
      setIsFree(nextIsFreeState)

      let nextFieldValue = ''
      if (nextIsFreeState) {
        // If the checkbox is going to be checked,
        // we need to clear the quantity field as an empty
        // string means unlimited quantity.
        nextFieldValue = '0'
      }

      if (priceRef.current) {
        updatePriceValue(nextFieldValue)
        priceRef.current.value = nextFieldValue
      }
    }

    const inputExtension = (
      <Checkbox
        ref={freeRef}
        label="Gratuit"
        checked={isFree}
        name={freeName}
        onChange={onCheckboxChange}
        disabled={disabled}
      />
    )

    return (
      <div ref={ref}>
        <TextInput
          ref={priceRef}
          className={className}
          labelClassName={smallLabel ? styles['input-layout-small-label'] : ''}
          required={!hideAsterisk}
          name={name}
          label={label}
          type="number"
          step="0.01"
          min={0}
          max={max}
          rightIcon={rightIcon}
          disabled={disabled}
          asterisk={!hideAsterisk}
          onChange={onTextInputChange}
          hasError={!!error}
          {...(showFreeCheckbox ? { InputExtension: inputExtension } : {})}
        />
      </div>
    )
  }
)
PriceInput.displayName = 'PriceInput'
