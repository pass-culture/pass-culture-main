import cn from 'classnames'
import { useField } from 'formik'

import { type EnumType } from 'commons/custom_types/utils'

import { RadioButton } from '../RadioButton/RadioButton'
import { FieldSetLayout } from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './RadioGroup.module.scss'

export const Direction = {
  VERTICAL: 'vertical',
  HORIZONTAL: 'horizontal',
} as const
// eslint-disable-next-line no-redeclare
export type Direction = EnumType<typeof Direction>

/**
 * Props for the RadioGroup component.
 */
interface RadioGroupProps {
  /**
   * The direction in which the radio buttons should be displayed.
   * @default Direction.VERTICAL
   */
  direction?: Direction
  /**
   * Whether the radio buttons are disabled.
   */
  disabled?: boolean
  /**
   * Whether to hide the footer containing error messages.
   * @default false
   */
  hideFooter?: boolean
  /**
   * The name of the radio group field.
   */
  name: string
  /**
   * The legend text for the radio group.
   */
  legend?: string
  /**
   * The group of radio button options.
   * Each item contains a label and a value.
   */
  group: {
    label: string
    value: string
  }[]
  /**
   * Custom CSS class for the radio group component.
   */
  className?: string
  /**
   * Whether to add a border around each radio button.
   */
  withBorder?: boolean
  /**
   * Callback function to handle changes in the radio group.
   */
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

/**
 * The RadioGroup component is a set of radio buttons grouped together under a common legend.
 * It integrates with Formik for form state management and provides customization options for layout and styling.
 *
 * ---
 * **Important: Always provide a legend for accessibility.**
 * Legends are essential for screen readers and provide context for the radio button group. If the legend should not be visible, use the `aria-label` attribute to provide an accessible label.
 * ---
 *
 * @param {RadioGroupProps} props - The props for the RadioGroup component.
 * @returns {JSX.Element} The rendered RadioGroup component.
 *
 * @example
 * <RadioGroup
 *   name="gender"
 *   legend="Select your gender"
 *   group={[
 *     { label: 'Male', value: 'male' },
 *     { label: 'Female', value: 'female' },
 *     { label: 'Other', value: 'other' },
 *   ]}
 *   direction={Direction.HORIZONTAL}
 * />
 *
 * @accessibility
 * - **Legend**: Always provide a meaningful legend using the `legend` prop for screen readers. This helps users understand the context of the radio group.
 * - **Keyboard Accessibility**: Users can navigate between radio buttons using arrow keys, which is standard behavior for radio groups.
 * - **ARIA Attributes**: The component uses a `fieldset` and `legend` to group related radio buttons, ensuring native browser support for screen readers and accessibility tools.
 * - **Error Handling**: Error messages are displayed in an accessible manner, helping users identify issues with their input.
 */
export const RadioGroup = ({
  direction = Direction.VERTICAL,
  disabled,
  hideFooter = false,
  group,
  name,
  legend,
  className,
  withBorder,
  onChange,
}: RadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })
  const hasError = meta.touched && !!meta.error

  return (
    <FieldSetLayout
      className={cn(
        styles['radio-group'],
        styles[`radio-group-${direction}`],
        className
      )}
      dataTestId={`wrapper-${name}`}
      error={hasError ? meta.error : undefined}
      hideFooter={hideFooter}
      legend={legend}
      name={`radio-group-${name}`}
      isOptional // There should always be an element selected in a radio group, thus it doesn't need to be marked as required
    >
      {group.map((item) => (
        <div className={styles['radio-group-item']} key={item.label}>
          <RadioButton
            disabled={disabled}
            label={item.label}
            name={name}
            value={item.value}
            withBorder={withBorder}
            hasError={hasError}
            fullWidth
            onChange={onChange}
            {...(hasError ? { ariaDescribedBy: `error-${name}` } : {})}
          />
        </div>
      ))}
    </FieldSetLayout>
  )
}
