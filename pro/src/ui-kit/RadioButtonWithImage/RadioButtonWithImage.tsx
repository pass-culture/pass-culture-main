import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'

import { ReactComponent as RadioOffIcon } from 'icons/ico-radio-off.svg'
import { ReactComponent as RadioOnIcon } from 'icons/ico-radio-on.svg'

import styles from './RadioButtonWithImage.module.scss'

export interface IRadioButtonWithImage {
  name: string
  isChecked: boolean
  Icon: FunctionComponent<
    SVGProps<SVGSVGElement> & { title?: string | undefined }
  >
  label: string
  description?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  className?: string
  disabled?: boolean
  value: string
}

const RadioButtonWithImage = ({
  name,
  isChecked,
  Icon,
  label,
  description,
  onChange,
  className,
  disabled = false,
  value,
}: IRadioButtonWithImage): JSX.Element => (
  <label
    className={cn(
      styles.button,
      description === undefined
        ? styles['layout-column']
        : styles['layout-row'],
      {
        [styles['is-selected']]: isChecked,
        [styles['is-disabled']]: disabled,
      },
      className
    )}
  >
    {isChecked ? (
      <RadioOnIcon className={styles['button-radio-on']} />
    ) : (
      <RadioOffIcon className={styles['button-radio-off']} />
    )}
    <Icon className={styles['button-icon']} />
    <input
      checked={isChecked}
      className={styles['button-radio']}
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
    />
    <div className={styles['button-text']}>
      <div>{label}</div>
      {description !== undefined && (
        <div className={styles['button-description']}>{description}</div>
      )}
    </div>
  </label>
)

export default RadioButtonWithImage
