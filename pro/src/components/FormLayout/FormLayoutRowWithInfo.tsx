import cn from 'classnames'
import React from 'react'

import style from './FormLayout.module.scss'
import Row from './FormLayoutRow'

interface IFormLayoutRowWithInfoProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  mdSpaceAfter?: boolean
  smSpaceAfter?: boolean
  sideComponent: JSX.Element | null
}

const RowWithInfo = ({
  children,
  className,
  inline,
  mdSpaceAfter,
  smSpaceAfter,
  sideComponent,
}: IFormLayoutRowWithInfoProps): JSX.Element => {
  return (
    <Row
      className={cn(className, style['form-layout-row-info'])}
      mdSpaceAfter={mdSpaceAfter}
      smSpaceAfter={smSpaceAfter}
    >
      <Row className={style['form-layout-row-info-field']} inline={inline}>
        {children}
      </Row>
      <div className={style['form-layout-row-info-info']}>
        <div className={style['form-layout-row-info-info-inner']}>
          {sideComponent && sideComponent}
        </div>
      </div>
    </Row>
  )
}

export default RowWithInfo
