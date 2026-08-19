import cn from 'classnames'
import type React from 'react'

import style from './SummaryLayout.module.scss'

export interface Description {
  text: string | number | React.ReactNode
  title?: string
  isBlock?: boolean
  stacked?: boolean
}

interface SummaryDescriptionListProps {
  className?: string
  descriptions: Description[]
  listDataTestId?: string
}

type DescriptionTextContentProps = Pick<
  Description,
  'text' | 'title' | 'isBlock'
>

const DescriptionTextContent = ({
  text,
  title,
  isBlock = false,
}: DescriptionTextContentProps) => (
  <>
    {title && <p className={style['summary-layout-row-title']}>{title} : </p>}
    {isBlock ? (
      <div className={style['summary-layout-row-description']}>{text}</div>
    ) : (
      <p className={style['summary-layout-row-description']}>{text}</p>
    )}
  </>
)

export const SummaryDescriptionList = ({
  className,
  descriptions,
  listDataTestId = '',
}: SummaryDescriptionListProps) => {
  if (descriptions.length === 0) {
    return null
  }

  if (descriptions.length === 1) {
    const { text, title, isBlock, stacked } = descriptions[0]
    return (
      <div
        className={cn(style['summary-layout-row'], className, {
          [style['summary-layout-row-stacked']]: stacked,
        })}
      >
        <DescriptionTextContent text={text} title={title} isBlock={isBlock} />
      </div>
    )
  }

  // dd/dt/dl is more semantic but less supported by assistive technologies
  // we use ul/li instead for now
  // TODO (igabriele, 2026-05-25): Use dl/dt/dd because this claim doesn't hold and ul/li are for genuine peer items.
  // The only exception is when term and definition are confusing which they shouldn't be in the first place (=> ":").
  // https://adrianroselli.com/2025/01/updated-brief-note-on-description-list-support.html (W3C Accessibility Expert)
  // https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dl#accessibility
  return (
    <ul data-testid={listDataTestId}>
      {descriptions.map(({ text, title, isBlock, stacked }, index) => (
        <li
          // biome-ignore lint/suspicious/noArrayIndexKey: Can't use anything else
          key={`${index + 1}`}
          className={cn(style['summary-layout-row'], className, {
            [style['summary-layout-row-stacked']]: stacked,
          })}
        >
          <DescriptionTextContent text={text} title={title} isBlock={isBlock} />
        </li>
      ))}
    </ul>
  )
}
