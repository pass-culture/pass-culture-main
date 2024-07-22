import cn from 'classnames'
import React from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import radioOffIcon from './assets/ico-radio-off.svg'
import radioOnIcon from './assets/ico-radio-on.svg'
import styles from './RadioButtonWithImage.module.scss'

interface RadioButtonWithImageProps {
  name: string
  isChecked: boolean
  icon: string
  label: string
  description?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  className?: string
  disabled?: boolean
  value: string
  dataTestid?: string
}

export const RadioButtonWithImage = ({
  name,
  isChecked,
  icon,
  label,
  description,
  onChange,
  className,
  disabled = false,
  value,
  dataTestid,
}: RadioButtonWithImageProps): JSX.Element => (
  <label
    className={cn(
      styles.button,
      description === undefined
        ? styles['layout-column']
        : styles['layout-row'],
      {
        [styles['is-selected'] ?? '']: isChecked,
        [styles['is-disabled'] ?? '']: disabled,
      },
      className
    )}
  >
    {isChecked ? (
      <SvgIcon
        alt=""
        src={radioOnIcon}
        className={styles['button-radio-on']}
        viewBox="0 0 16 16"
        width="16"
      />
    ) : (
      <SvgIcon
        alt=""
        src={radioOffIcon}
        className={styles['button-radio-off']}
        viewBox="0 0 16 16"
        width="16"
      />
    )}

    <SvgIcon src={icon} className={styles['button-icon']} alt="" />

    <input
      checked={isChecked}
      className="visually-hidden"
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
      data-testid={dataTestid}
    />

    <span className={styles['button-text']}>
      <span>{label}</span>
      {description !== undefined && (
        <span className={styles['button-description']}>{description}</span>
      )}
    </span>
  </label>
)
