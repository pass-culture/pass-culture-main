/**
 * Props for the SvgIcon component.
 */
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
  /**
   * Custom CSS class for additional styling of the SVG.
   */
  className?: string
  /**
   * The SVG viewBox attribute.
   * This must be provided if the SVG viewBox is known to be different from 0 0 48 48.
   * Otherwise, the SVG won't be displayed correctly.
   * @default '0 0 48 48'
   */
  viewBox?: string
  /**
   * The width of the SVG icon.
   */
  width?: string
  /**
   * Inline styles for the SVG icon.
   */
  style?: React.CSSProperties
  /**
   * The test id of the SVG icon.
   */
  'data-testid'?: string
}

/**
 * The SvgIcon component is used to display SVG icons that can change color and have a text alternative.
 * To use this component, the SVG must:
 * - Have an `id="icon"` on the path/group that you want to display.
 * - Have `fill="currentColor"` on the elements that use the CSS color of the parent.
 * - If the viewBox is different from `0 0 48 48`, you must pass it as a prop.
 *
 * ---
 * **Important: Always provide an `alt` attribute for meaningful icons to ensure accessibility.**
 * If the icon is purely decorative, leave the `alt` attribute empty or undefined.
 * ---
 *
 * @param {SvgIconProps} props - The props for the SvgIcon component.
 * @returns {JSX.Element} The rendered SvgIcon component.
 *
 * @example
 * <SvgIcon src="/icons/check.svg" alt="Checkmark" width="24" />
 *
 * @accessibility
 * - **Alt Text**: Provide meaningful alt text for screen readers when the icon conveys important information. Use `aria-hidden` for decorative icons.
 */
export const SvgIcon = ({
  src,
  alt = '',
  className,
  viewBox = '0 0 48 48',
  width,
  style,
  'data-testid': dataTestid,
}: SvgIconProps) => {
  return (
    <svg
      className={className}
      viewBox={viewBox}
      {...(alt ? { 'aria-label': alt, role: 'img' } : { 'aria-hidden': true })}
      {...(width ? { width } : {})}
      {...(dataTestid ? { 'data-testid': dataTestid } : {})}
      style={style}
    >
      <use xlinkHref={`${src}#icon`} />
    </svg>
  )
}
