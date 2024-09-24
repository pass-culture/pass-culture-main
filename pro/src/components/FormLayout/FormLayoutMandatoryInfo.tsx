import cn from 'classnames'
import React from 'react'
import { useTranslation } from 'react-i18next'

import style from './FormLayout.module.scss'

interface FormLayoutMandatoryInfoProps {
  className?: string
}

export const MandatoryInfo = ({
  className,
}: FormLayoutMandatoryInfoProps): JSX.Element => {
  const { t } = useTranslation('common')
  return (
    <p className={cn(style['mandatory-info'], className)}>
      {t('mandatory_fields')}
    </p>
  )
}
