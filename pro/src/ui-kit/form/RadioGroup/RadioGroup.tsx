import cn from 'classnames'
import { useField } from 'formik'

import { RadioButton } from '../RadioButton/RadioButton'
import { BaseRadioProps, RadioVariant } from '../shared/BaseRadio/BaseRadio'
import {
  FieldSetLayout,
  FieldSetLayoutProps,
} from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './RadioGroup.module.scss'

type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = Pick<
  T,
  Exclude<keyof T, Keys>
> &
  {
    [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>>
  }[Keys]

/**
 * Props for the RadioGroup component.
 */
export type RadioGroupProps = RequireAtLeastOne<
  {
    /**
     * Whether the radio buttons are disabled.
     */
    disabled?: boolean
    /**
     * The name of the radio group field.
     */
    name: string
    /**
     * The legend of the `fieldset`. If this prop is empty, the `describedBy` must be used.
     */
    legend?: FieldSetLayoutProps['legend']
    /**
     * A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.
     */
    describedBy?: string
    /**
     * The group of radio button options.
     * Each item contains a label and a value.
     * The label is what's displayed while the value is used as an identifier.
     */
    group: {
      label: string | JSX.Element
      value: string
      icon?: BaseRadioProps['icon']
      iconPosition?: BaseRadioProps['iconPosition']
      description?: BaseRadioProps['description']
      childrenOnChecked?: JSX.Element
    }[]
    /**
     * Custom CSS class applied to the group's `fieldset` element.
     */
    className?: string
    /**
     * Variant of the radio inputs styles within the group.
     */
    variant?: RadioVariant.BOX
    /**
     * Callback function to handle changes in the radio group.
     */
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
    /**
     * Whether or not the group is optional.
     */
    isOptional?: boolean
    /**
     * How the radio buttons are displayed within the group.
     * If "default", buttons are displayed in column.
     * If "inline", buttons are displayed in a row.
     * If "inline-grow", buttons are displayed in a row, and they share the available width.
     */
    displayMode?: 'default' | 'inline' | 'inline-grow'
  },
  'legend' | 'describedBy'
>

/**
 * The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.
 * It integrates with Formik for form state management and provides customization options for layout and styling.
 *
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
 * />
 *
 * @accessibility
 * - **Fieldset**: The component uses a `fieldset` element and a `legend` element to group related radio buttons together. Always provide a meaningful legend using the `legend` prop as it provides context for assistive technologies.
 * - **Name**: The `name` prop is used as a link in-between the inputs of the group. It should be unique on the page at any time.
 */
export const RadioGroup = ({
  disabled,
  group,
  name,
  legend,
  describedBy,
  className,
  variant,
  onChange,
  isOptional = true,
  displayMode,
}: RadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })
  const hasError = meta.touched && !!meta.error

  return (
    <FieldSetLayout
      className={cn(styles['radio-group'], className)}
      dataTestId={`wrapper-${name}`}
      error={hasError ? meta.error : undefined}
      legend={legend}
      name={`radio-group-${name}`}
      ariaDescribedBy={describedBy}
      isOptional={isOptional}
      hideFooter
    >
      <div className={styles[`radio-group-display-${displayMode}`]}>
        {group.map((item) => (
          <div className={styles['radio-group-item']} key={item.value}>
            <RadioButton
              disabled={disabled}
              label={item.label}
              name={name}
              value={item.value}
              variant={variant}
              hasError={hasError}
              onChange={onChange}
              icon={item.icon}
              iconPosition={item.iconPosition}
              description={item.description}
              {...(hasError ? { ariaDescribedBy: `error-${name}` } : {})}
              childrenOnChecked={item.childrenOnChecked}
            />
          </div>
        ))}
      </div>
    </FieldSetLayout>
  )
}
