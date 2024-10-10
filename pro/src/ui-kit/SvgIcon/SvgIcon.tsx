import React from 'react'

export interface SvgIconProps {
  /**
   * The SVG src path.
   * SVGs are usually imported as React components from the pro/src/icons folder.
   * To use them, you must import the SVG and pass it as the src prop.
   */
  src: string
  /**
   * An alternative text for the icon.
   * If provided and non-empty, the SVG will have a role="img" and an aria-label attribute.
   * If undefined or empty, the SVG will have an aria-hidden attribute instead, as a
   * decorative icon.
   */
  alt?: string
  className?: string
  /**
   * The SVG viewBox attribute.
   * This must be provided if the SVG viewBox is known to be different from 0 0 48 48.
   * Otherwise, the SVG wont be displayed correctly.
   */
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
  alt = '',
  className,
  viewBox = '0 0 48 48',
  width,
  style,
}: SvgIconProps) => {
  return (
    <svg
      className={className}
      viewBox={viewBox}
      {...(alt ? { 'aria-label': alt, role: 'img' } : { 'aria-hidden': true })}
      {...(width ? { width } : {})}
      style={style}
    >
      <use xlinkHref={`${src}#icon`} />
    </svg>
  )
}
