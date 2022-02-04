import cn from 'classnames'
import React from 'react'

import FieldError from '../FieldError'

import styles from './FieldSetLayout.module.scss'

interface IFieldSetLayoutProps {
  children: React.ReactNode
  legend?: string
  className?: string
  error?: string
  name: string
  hideFooter?: boolean
}

const FieldSetLayout = ({
  children,
  legend,
  className,
  error,
  name,
  hideFooter = false,
}: IFieldSetLayoutProps): JSX.Element => (
  <fieldset className={cn(styles['fieldset-layout'], className)}>
    {legend && (
      <legend className={styles['fieldset-layout-legend']}>{legend}</legend>
    )}

    <div>{children}</div>

    {!hideFooter && (
      <div className={styles['fieldset-layout-error']}>
        {!!error && <FieldError name={name}>{error}</FieldError>}
      </div>
    )}
  </fieldset>
)

export default FieldSetLayout
