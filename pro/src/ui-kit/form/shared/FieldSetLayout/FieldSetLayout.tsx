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
  dataTestId?: string
}

const FieldSetLayout = ({
  children,
  legend,
  className,
  error,
  name,
  hideFooter = false,
  dataTestId,
}: IFieldSetLayoutProps): JSX.Element => {
  return (
    <fieldset
      className={cn(styles['fieldset-layout'], className)}
      data-testid={dataTestId}
    >
      {legend && (
        <legend className={styles['fieldset-layout-legend']}>{legend}</legend>
      )}

      <div> {children} </div>

      {!hideFooter && (
        <div className={styles['fieldset-layout-error']}>
          {!!error && <FieldError name={name}>{error}</FieldError>}
        </div>
      )}
    </fieldset>
  )
}

export default FieldSetLayout
