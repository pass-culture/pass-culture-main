import React from 'react'

import { Typography } from 'ui-kit'

import styles from './FormSection.module.scss'

interface IFormSectionProps {
    title: string;
    subtitle?: string;
    className?: string;
}

const FormSection: React.FC<IFormSectionProps> = ({
  title,
  subtitle,
  className,
  children,
}): JSX.Element => {
  return (
    <section className={className}>
      <div className={styles['form-section-header']}>
        <Typography
          level='h3'
          title={title}
        />
        {subtitle ? (
          <p className={styles.subtitle}>
            {subtitle}
          </p>
        ) : null}
      </div>
      {children}
    </section>
  )
}

export default FormSection
