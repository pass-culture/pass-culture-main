import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import styles from './RadioButton.module.scss'

type CommonProps = Partial<React.InputHTMLAttributes<HTMLInputElement>> & {
  name: string
  label: string
  value: string
  className?: string
  checked?: boolean
  ariaDescribedBy?: string
  variant?: 'DEFAULT' | 'DETAILED'
}

// ---------------
// Variant DEFAULT
// ---------------

type DefaultVariantProps = CommonProps & {
  variant?: 'DEFAULT'
  description?: never
  icon?: never
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// ---------------
// Variant DETAILED
// ---------------

// Description is optional
type DetailedWithDescriptionProps = {
  description?: string
}

// Right element is an "icon" string
type DetailedWithIconProps = DetailedWithDescriptionProps & {
  icon: string
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// Right element is tag Element
type DetailedWithTagProps = DetailedWithDescriptionProps & {
  icon?: never
  tag: JSX.Element // TODO: restrict to a <Tag/> Element when it'll be ready in DS
  text?: never
  image?: never
  imageSize?: never
}

// Right element is simple "text" string
type DetailedWithTextProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text: string
  image?: never
  imageSize?: never
}

// Right element is an "image", and can eventually have a size
type DetailedWithImageProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text?: never
  image: string
  imageSize?: 'S' | 'M' | 'L'
}

type DetailedWithNothingProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// Specific to DETAILED variant
type DetailedVariantProps = CommonProps & {
  variant: 'DETAILED'
} & (
    | DetailedWithIconProps
    | DetailedWithTagProps
    | DetailedWithTextProps
    | DetailedWithImageProps
    | DetailedWithNothingProps
  )

// Final assembled type for RadioButton Component
export type RadioButtonProps = DefaultVariantProps | DetailedVariantProps

export const RadioButton = forwardRef(
  (
    {
      label,
      variant = 'DEFAULT',
      className,
      ariaDescribedBy,
      description,
      icon,
      tag,
      text,
      image,
      imageSize = 'M',
      ...props
    }: RadioButtonProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const id = useId()
    const descriptionId = useId()

    let describedBy = ariaDescribedBy ? ariaDescribedBy : ''
    describedBy += description ? ` ${descriptionId}` : ''

    return (
      <>
        <div
          className={cn(
            styles['radio-button'],
            {
              [styles[`variant-detailed`]]: variant === 'DETAILED',
              // [styles[`has-children`]]: childrenOnChecked,
              [styles[`is-checked`]]: props.checked,
              [styles[`is-disabled`]]: props.disabled,
            },
            className
          )}
        >
          <label htmlFor={id} className={styles['radio-button-label']}>
            <input
              type="radio"
              {...props}
              className={styles[`radio-button-input`]}
              aria-describedby={describedBy}
              id={id}
              ref={ref}
            />
            {label}
            {/* {description && <p>Description = {description} </p>} */}
          </label>
        </div>
        {/* {childrenOnChecked && props.checked && (
          <div className={styles['radio-button-children-on-checked']}>
            {childrenOnChecked}
          </div>
        )} */}
      </>
    )
  }
)
RadioButton.displayName = 'RadioButton'
