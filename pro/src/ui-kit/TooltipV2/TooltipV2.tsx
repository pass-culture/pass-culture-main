import classNames from 'classnames'
import React, { useId, useLayoutEffect, useRef, useState } from 'react'

import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './TooltipV2.module.scss'

const allowedTooltipTriggerTypes: JSX.Element['type'] = [
  'button',
  'a',
  'input',
  'Button',
  'ButtonLink',
  'ListIconButton',
]

/**
 * Props for the Tooltip component.
 */
export type TooltipV2Props = {
  /** Interactive element that triggers the opening of the tooltip panel. */
  children: JSX.Element
  /** Tooltip panel content. */
  content: JSX.Element
}

/**
 * The Tooltip component is used to display additional information when a user hovers over or focuses on an element.
 * It wraps around a child element that must be an interactive element.
 *
 * @param {TooltipV2Props} props - The props for the Tooltip component.
 * @returns {JSX.Element} The rendered Tooltip component.
 *
 * @example
 * <Tooltip content="This is a tooltip">
 *   <button>Hover over me</button>
 * </Tooltip>
 *
 * @accessibility
 * - Tooltips are not accessible to touch interfaces, thus it should be avoided.
 */

export function TooltipV2({ children, content }: TooltipV2Props) {
  if (
    !allowedTooltipTriggerTypes.includes(children.type) &&
    !allowedTooltipTriggerTypes.includes(children.type.displayName)
  ) {
    //  If the tooltip is not placed on a focusable element, the information it bears is not accessible to keyboard users
    throw Error(
      `The tooltip immediate child must be an interactive element of one of the following types : ${allowedTooltipTriggerTypes.join(', ')}.`
    )
  }

  const { isTooltipHidden, ...tooltipProps } = useTooltipProps({})
  const [tooltipContentRect, setTooltipContentRect] = useState<DOMRect | null>(
    null
  )
  const tooltipId = useId()
  const panelRef = useRef<HTMLDivElement>(null)

  //  Add the tooltip trigger mandatory attributes to the intractive element passed as child
  const tooltipTrigger = React.cloneElement(children, {
    onFocus: tooltipProps.onFocus,
    onBlur: tooltipProps.onBlur,
    'aria-describedby': tooltipId,
  })

  useLayoutEffect(() => {
    //  Get the initial dimentions of the tooltip panel before showing it on the screen
    if (panelRef.current) {
      setTooltipContentRect(panelRef.current.getBoundingClientRect())
    }
  }, [isTooltipHidden])

  //  Prevent the panel from being outlide the screen
  const offsetLeft = tooltipContentRect
    ? tooltipContentRect.width + tooltipContentRect.x >
      document.body.clientWidth
      ? document.body.clientWidth -
        tooltipContentRect.width -
        tooltipContentRect.x
      : tooltipContentRect.x < 0
        ? -tooltipContentRect.x
        : 0
    : 0

  //  Position the tooltip above its trigger
  const offsetTop = tooltipContentRect ? -tooltipContentRect.height : 0

  return (
    <div className={styles['tooltip-container']}>
      <div
        className={styles['tooltip']}
        onMouseOver={tooltipProps.onMouseOver}
        onMouseOut={tooltipProps.onMouseOut}
      >
        {tooltipTrigger}
        <div
          id={tooltipId}
          ref={panelRef}
          style={{
            top: '0px',
            transform: `translate(${offsetLeft}px, ${offsetTop}px)`,
          }}
          className={classNames(
            { [styles['visually-hidden']]: isTooltipHidden },
            styles['tooltip-content']
          )}
          role="tooltip"
          aria-hidden="true"
        >
          <div className={styles['tooltip-content-panel']}>{content}</div>
        </div>
      </div>
    </div>
  )
}
