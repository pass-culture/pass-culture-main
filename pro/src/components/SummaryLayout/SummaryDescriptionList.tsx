import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

export interface Description {
  text: string | number | React.ReactNode
  title?: string
}

interface SummaryDescriptionListProps {
  className?: string
  descriptions: Description[]
}

const DescriptionTextContent = ({ text, title }: Description) => (
  <>
    {title && (
      <span className={style['summary-layout-row-title']}>{title} : </span>
    )}
    <span className={style['summary-layout-row-description']}>{text}</span>
  </>
)

export const SummaryDescriptionList = ({
  className,
  descriptions,
}: SummaryDescriptionListProps) => {
  if (descriptions.length === 0) {
    return null
  }

  if (descriptions[0] && descriptions.length === 1) {
    const { text, title } = descriptions[0]
    return (
      <div className={cn(style['summary-layout-row'], className)}>
        <DescriptionTextContent text={text} title={title} />
      </div>
    )
  }

  // dd/dt/dl is more semantic but less supported by assistive technologies
  // we use ul/li instead for now
  return (
    <ul>
      {descriptions.map(({ text, title }, index) => (
        <li key={index} className={cn(style['summary-layout-row'], className)}>
          <DescriptionTextContent text={text} title={title} />
        </li>
      ))}
    </ul>
  )
}
