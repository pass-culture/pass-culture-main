import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink, LinkProps } from 'ui-kit/Button/ButtonLink'

import styles from './LinkNodes.module.scss'

/**
 * Represents a single link.
 */
export type Link = {
  /**
   * The icon to display alongside the link.
   */
  icon?: {
    src: string
    alt: string
  } | null
  /**
   * The destination URL for the link.
   */
  href: string
  /**
   * The label text for the link.
   */
  label: string
  /**
   * Specifies where to open the linked document.
   */
  target?: string
  /**
   * Indicates if the link is external.
   */
  isExternal?: boolean
  /**
   * Indicates if the link is a section link within the page.
   */
  isSectionLink?: boolean
  /**
   * Callback function triggered when the link is clicked.
   */
  onClick?: () => void
  /**
   * ARIA label for accessibility purposes.
   */
  'aria-label'?: string
}

/**
 * Props for the LinkNodes component.
 */
interface LinkNodesProps {
  /**
   * An array of link objects to be displayed.
   */
  links?: Link[]
}

/**
 * The LinkNode component is used to create a single link with an optional icon.
 * It supports internal, external, and section links.
 *
 * @param {Link} props - The properties of the link.
 * @returns {React.ReactNode} The rendered link as a ButtonLink.
 */
export const LinkNode = ({
  icon,
  href,
  label,
  isExternal,
  isSectionLink,
  onClick,
  'aria-label': ariaLabel,
}: Link): React.ReactNode => {
  const forwardLink: LinkProps = { to: href, isExternal, isSectionLink }
  if (ariaLabel) {
    forwardLink['aria-label'] = ariaLabel
  }
  return (
    <ButtonLink
      {...forwardLink}
      //  If the link is external, the link automatically opens in a new tab
      opensInNewTab={isExternal}
      icon={isExternal ? fullLinkIcon : (icon?.src ?? fullNextIcon)}
      className={styles['bi-link']}
      onClick={onClick}
    >
      {label}
    </ButtonLink>
  )
}

/**
 * The LinkNodes component is used to render one or more links.
 * It displays a list of links when there are multiple links or a single link if only one is provided.
 *
 * @param {LinkNodesProps} props - The props for the LinkNodes component.
 * @returns {React.ReactNode | React.ReactNode[]} The rendered LinkNode(s).
 *
 * @example
 * <LinkNodes
 *   links={[{
 *     href: '/home',
 *     label: 'Home',
 *     isExternal: false
 *   }]}
 * />
 */
export const LinkNodes = ({
  links = [],
}: LinkNodesProps): React.ReactNode | React.ReactNode[] => {
  if (links.length > 1) {
    return (
      <ul>
        {links.map((link) => {
          return (
            <li key={link.href} className={styles['bi-link-item']}>
              <LinkNode {...link} />
            </li>
          )
        })}
      </ul>
    )
  }
  return links[0] && <LinkNode {...links[0]} />
}
