import cn from 'classnames'
import { isArray } from 'lodash'
import React from 'react'

import style from './FormLayout.module.scss'
import Row from './FormLayoutRow'

interface IFormLayoutRowWithInfoProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  inline?: boolean
  lgSpaceAfter?: boolean
  smSpaceAfter?: boolean
}

const RowWithInfo = ({
  children,
  className,
  inline,
  lgSpaceAfter,
  smSpaceAfter,
}: IFormLayoutRowWithInfoProps): JSX.Element => {
  if (!isArray(children)) {
    children = [children]
  }
  const [fieldBlock, infoBlock] = children

  return infoBlock ? (
    <Row
      className={cn(className, style['form-layout-row-info'])}
      lgSpaceAfter={lgSpaceAfter}
      smSpaceAfter={smSpaceAfter}
    >
      <Row className={style['form-layout-row-info-field']} inline={inline}>
        {fieldBlock}
      </Row>
      <div className={style['form-layout-row-info-info']}>
        <div className={style['form-layout-row-info-info-inner']}>
          {infoBlock}
        </div>
      </div>
    </Row>
  ) : (
    <Row
      className={className}
      inline={inline}
      lgSpaceAfter={lgSpaceAfter}
      smSpaceAfter={smSpaceAfter}
    >
      {fieldBlock}
    </Row>
  )
}

export default RowWithInfo
