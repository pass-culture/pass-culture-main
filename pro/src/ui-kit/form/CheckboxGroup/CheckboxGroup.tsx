import classNames from 'classnames'
import { useField } from 'formik'

import { RequireAtLeastOne } from '../RadioGroup/RadioGroup'
import { CheckboxVariant } from '../shared/BaseCheckbox/BaseCheckbox'
import { FieldSetLayout } from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './CheckboxGroup.module.scss'
import { CheckboxGroupItem } from './CheckboxGroupItem'

type CheckboxGroupProps = RequireAtLeastOne<
  {
    groupName: string
    legend?: string | React.ReactNode
    describedBy?: string
    group: {
      name: string
      label: string | React.ReactNode
      icon?: string
      onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
      childrenOnChecked?: JSX.Element
      shouldShowChildren?: boolean
    }[]
    disabled?: boolean
    isOptional?: boolean
    variant?: CheckboxVariant
    inline?: boolean
    hideAsterisk?: boolean
  },
  'legend' | 'describedBy'
>

export const CheckboxGroup = ({
  group,
  groupName,
  legend,
  describedBy,
  disabled,
  isOptional,
  variant,
  inline = false,
  hideAsterisk,
}: CheckboxGroupProps): JSX.Element => {
  const [, meta, helpers] = useField({ name: groupName })
  const hasError = meta.touched && !!meta.error

  return (
    <FieldSetLayout
      error={hasError ? meta.error : undefined}
      legend={legend}
      name={groupName}
      ariaDescribedBy={describedBy}
      isOptional={isOptional}
      hideFooter
      hideAsterisk={hideAsterisk}
    >
      <div
        className={classNames(styles['checkbox-group'], {
          [styles['inline']]: inline,
        })}
      >
        {group.map((item) => (
          <div className={styles['checkbox-group-item']} key={item.name}>
            <CheckboxGroupItem
              icon={item.icon}
              hasError={hasError}
              label={item.label}
              name={item.name}
              setGroupTouched={() =>
                !meta.touched ? helpers.setTouched(true) : null
              }
              disabled={disabled}
              onChange={item.onChange}
              {...(hasError ? { ariaDescribedBy: `error-${groupName}` } : {})}
              variant={variant}
              childrenOnChecked={item.childrenOnChecked}
              shouldShowChildren={item.shouldShowChildren}
            />
          </div>
        ))}
      </div>
    </FieldSetLayout>
  )
}
