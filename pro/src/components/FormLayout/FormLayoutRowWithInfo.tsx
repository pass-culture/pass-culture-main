import cn from 'classnames'
import type React from 'react'

import style from './FormLayout.module.scss'
import { Row } from './FormLayoutRow'

interface FormLayoutRowWithInfoProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  lgSpaceAfter?: boolean
  mdSpaceAfter?: boolean
  smSpaceAfter?: boolean
  sideComponent: JSX.Element | null
  testId?: string
}

export const RowWithInfo = ({
  children,
  className,
  inline,
  lgSpaceAfter,
  mdSpaceAfter,
  smSpaceAfter,
  sideComponent,
  testId,
}: FormLayoutRowWithInfoProps): JSX.Element => {
  return (
    <Row
      className={cn(className, style['form-layout-row-info'])}
      lgSpaceAfter={lgSpaceAfter}
      mdSpaceAfter={mdSpaceAfter}
      smSpaceAfter={smSpaceAfter}
      testId={testId}
    >
      <Row className={style['form-layout-row-info-field']} inline={inline}>
        {children}
      </Row>
      <div className={style['form-layout-row-info-info']}>
        <div className={style['form-layout-row-info-info-inner']}>
          {sideComponent}
        </div>
      </div>
    </Row>
  )
}
