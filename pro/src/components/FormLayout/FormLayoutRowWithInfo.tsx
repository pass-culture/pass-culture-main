import cn from 'classnames'
import type React from 'react'
import { useId } from 'react'

import { FormLayoutSideComponentContextProvider } from '@/commons/context/FormLayoutSideComponentContext/FormLayoutSideComponentContext'

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
  const sideComponentId = useId()
  return (
    <Row
      className={cn(className, style['form-layout-row-info'])}
      lgSpaceAfter={lgSpaceAfter}
      mdSpaceAfter={mdSpaceAfter}
      smSpaceAfter={smSpaceAfter}
      testId={testId}
    >
      <FormLayoutSideComponentContextProvider describedById={sideComponentId}>
        <Row
          className={style['form-layout-row-info-field']}
          inline={inline}
          describedById={sideComponentId}
        >
          {children}
        </Row>
      </FormLayoutSideComponentContextProvider>
      <div className={style['form-layout-row-info-info']} id={sideComponentId}>
        <div className={style['form-layout-row-info-info-inner']}>
          {sideComponent}
        </div>
      </div>
    </Row>
  )
}
