import React from 'react'

export interface SvgIconProps {
  src: string
  alt: string
  className?: string
  viewBox?: string
  width?: string
  style?: React.CSSProperties
}

// This is component is used to display svg icons that can change color and have a text alternative
// To use it, the SVG must:
// - have an id="icon" on the path/group that you want to display
// - have fill="currentColor" on the elements that use the CSS color of the parent
// - if the viewBox is different from 0 0 48 48, you must pass it as a prop
export const SvgIcon = ({
  src,
  alt,
  className,
  viewBox = '0 0 48 48',
  width,
  style,
}: SvgIconProps) => {
  return (
    <svg
      className={className}
      viewBox={viewBox}
      {...(alt !== ''
        ? { 'aria-label': alt, role: 'img' }
        : { 'aria-hidden': true })}
      {...(width ? { width } : {})}
      style={style}
    >
      <use xlinkHref={`${src}#icon`}></use>
    </svg>
  )
}
