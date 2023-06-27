import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'

import RadioOffIcon from 'icons/ico-radio-off.svg'
import RadioOnIcon from 'icons/ico-radio-on.svg'

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
  dataTestid?: string
  transparent?: boolean
}

const RadioButtonWithImage = ({
  name,
  isChecked,
  label,
  description,
  onChange,
  className,
  disabled = false,
  value,
  dataTestid,
  transparent = false,
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
    <input
      checked={isChecked}
      className={styles['button-radio']}
      disabled={disabled}
      name={name}
      onChange={onChange}
      type="radio"
      value={value}
      data-testid={dataTestid}
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
