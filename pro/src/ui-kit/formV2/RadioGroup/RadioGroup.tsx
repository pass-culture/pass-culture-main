import cn from 'classnames'

import {
  RadioButton,
  RadioButtonProps,
} from 'design-system/RadioButton/RadioButton'
import { FieldSetLayout } from 'ui-kit/form/shared/FieldSetLayout/FieldSetLayout'

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
    legend: React.ReactNode
    /**
     * A reference to the text element that describes the radio group. If this prop is empty, the `legend` must be used.
     */
    describedBy?: string
    /**
     * The group of radio button options.
     * Each item contains a label and a value.
     * The label is what's displayed while the value is used as an identifier.
     */
    group: Omit<
      RadioButtonProps,
      'checked' | 'name' | 'onChange' | 'disabled'
    >[]
    /**
     * Selected option, required if the group is non-controlled
     */
    checkedOption?: string
    /**
     * Custom CSS class applied to the group's `fieldset` element.
     */
    className?: string
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
    variant?: RadioButtonProps['variant']
  },
  'legend' | 'describedBy'
>

/**
 * The RadioGroup component is a set of radio buttons grouped together under a common `fieldset`.
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
  onChange,
  isOptional = true,
  displayMode,
  checkedOption,
  variant,
}: RadioGroupProps): JSX.Element => {
  return (
    <FieldSetLayout
      className={cn(styles['radio-group'], className)}
      dataTestId={`wrapper-${name}`}
      legend={legend}
      name={`radio-group-${name}`}
      ariaDescribedBy={describedBy}
      isOptional={isOptional}
      hideFooter
    >
      <div className={styles[`radio-group-display-${displayMode}`]}>
        {group.map((item) => {
          const itemVariant = variant || item.variant

          const radioButtonProps = {
            disabled: disabled,
            name: name,
            onChange: onChange,
            checked: checkedOption === item.value,
          }

          return (
            <div className={styles['radio-group-item']} key={item.value}>
              {itemVariant === 'default' ? (
                <RadioButton
                  {...item}
                  {...radioButtonProps}
                  variant="default"
                  description={undefined}
                  asset={undefined}
                  collapsed={undefined}
                />
              ) : (
                <RadioButton
                  {...item}
                  {...radioButtonProps}
                  variant="detailed"
                />
              )}
            </div>
          )
        })}
      </div>
    </FieldSetLayout>
  )
}
