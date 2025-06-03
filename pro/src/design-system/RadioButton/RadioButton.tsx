import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { Tag, TagProps } from 'design-system/Tag/Tag'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './RadioButton.module.scss'

/**
 * Common props for all RadioButton
 * @property label - Label displayed next to the button (required)
 * @property name - Radio group name (required)
 * @property value - Button value (required)
 * @property checked - If the button is selected
 * @property variant - Display variant ('default' or 'detailed')
 * @property sizing - Component size ('hug' or 'fill')
 * @property disabled - If the radio is disabled
 * @property onChange - Event handler for change
 * @property onBlur - Event handler for blur
 */
type CommonProps = {
  /** Label displayed next to the radio */
  label: string
  /** Radio group name */
  name: string
  /** radio value */
  value: string
  /** If the radio is selected */
  checked?: boolean
  /** Display variant */
  variant?: 'default' | 'detailed'
  /** Component size */
  sizing?: 'hug' | 'fill'
  /** If the radio is disabled */
  disabled?: boolean
  /** Event handler for change */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  /** Event handler for blur */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
}

// ---------------
// Variant default
// ---------------

/**
 * Props for the default variant
 * @property description - Never used here
 * @property collapsed - Never used here
 * @property icon - Never used here
 * @property tag - Never used here
 * @property text - Never used here
 * @property image - Never used here
 * @property imageSize - Never used here
 */
type DefaultVariantProps = CommonProps & {
  variant?: 'default'
  sizing?: 'hug'
  description?: never
  collapsed?: never
  icon?: never
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// ---------------
// Variant detailed
// ---------------

/**
 * Props for the detailed variant
 * @property description - Optional description (only for the detailed variant)
 * @property collapsed - JSX element displayed if checked
 */
type DetailedWithDescriptionProps = {
  /** Optional description (only for the detailed variant) */
  description?: string
  /** JSX element displayed if checked */
  collapsed?: JSX.Element
}

// Right element is an "icon" string
/**
 * detailed variant with icon on the right
 * @property icon - Icon name
 */
type DetailedWithIconProps = DetailedWithDescriptionProps & {
  /** Icon name */
  icon: string
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// Right element is a <Tag/>
/**
 * detailed variant with tag on the right
 * @property tag - TagProps
 */
type DetailedWithTagProps = DetailedWithDescriptionProps & {
  icon?: never
  tag: TagProps
  text?: never
  image?: never
  imageSize?: never
}

// Right element is simple "text" string
/**
 * detailed variant with text on the right
 * @property text - Text to display
 */
type DetailedWithTextProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  /** Text to display */
  text: string
  image?: never
  imageSize?: never
}

// Right element is an "image", and can eventually have a size
/**
 * detailed variant with image on the right
 * @property image - Image URL
 * @property imageSize - Image size ('S', 'M', 'L')
 */
type DetailedWithImageProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text?: never
  /** Image URL */
  image: string
  /** Image size ('S', 'M', 'L') */
  imageSize?: 'S' | 'M' | 'L'
}

/**
 * detailed variant with nothing on the right
 */
type DetailedWithNothingProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// Specific to detailed variant
/**
 * Props specific to the detailed variant
 * @property variant - Must be 'detailed'
 */
type DetailedVariantProps = CommonProps & {
  variant: 'detailed'
} & (
    | DetailedWithIconProps
    | DetailedWithTagProps
    | DetailedWithTextProps
    | DetailedWithImageProps
    | DetailedWithNothingProps
  )

// Final assembled type for RadioButton Component
/**
 * Props for the RadioButton component (default or detailed)
 */
type RadioButtonProps = DefaultVariantProps | DetailedVariantProps

export const RadioButton = forwardRef(
  (
    {
      label,
      value,
      variant = 'default',
      sizing,
      description,
      collapsed,
      icon,
      tag,
      text,
      image,
      imageSize = 'S',
      disabled,
      checked,
      onChange,
      onBlur,
    }: RadioButtonProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const id = useId()

    const isVariantDetailed = variant === 'detailed'

    return (
      <>
        <div
          className={cn(styles['radio-button'], {
            [styles['sizing-fill']]: sizing === 'fill',
            [styles['variant-detailed']]: isVariantDetailed,
            [styles['is-collapsed']]: collapsed,
            [styles['is-checked']]: checked,
            [styles['is-disabled']]: disabled,
          })}
        >
          <label htmlFor={id} className={styles['radio-button-label']}>
            <input
              type="radio"
              value={value}
              className={styles[`radio-button-input`]}
              id={id}
              ref={ref}
              {...(checked !== undefined ? { checked } : {})}
              onChange={onChange}
              onBlur={onBlur}
              disabled={disabled}
            />
            <div>
              {label}
              {description && isVariantDetailed && (
                <p className={styles['description']}>{description}</p>
              )}
            </div>
            {isVariantDetailed && (
              <>
                {tag && (
                  <div className={styles['right-tag']}>
                    <Tag {...tag} />
                  </div>
                )}
                {icon && (
                  <div className={styles['right-icon']}>
                    <SvgIcon
                      src={icon}
                      alt=""
                      className={styles['right-icon-svg']}
                    />
                  </div>
                )}
                {text && <div className={styles['right-text']}>{text}</div>}
                {image && (
                  <div className={styles['right-image']}>
                    <img
                      src={image}
                      alt=""
                      className={cn({
                        [styles['right-image-img-small']]: imageSize === 'S',
                        [styles['right-image-img-medium']]: imageSize === 'M',
                        [styles['right-image-img-large']]: imageSize === 'L',
                      })}
                    />
                  </div>
                )}
              </>
            )}
          </label>
          {collapsed && isVariantDetailed && checked && (
            <div className={styles['collapsed']}>{collapsed}</div>
          )}
        </div>
      </>
    )
  }
)
RadioButton.displayName = 'RadioButton'
