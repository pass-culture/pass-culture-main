import * as TabsPrimitive from '@radix-ui/react-tabs'
import cn from 'classnames'
import { Link } from 'react-router-dom'

import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './Tabs.module.scss'

/**
 * Represents a single tab in the Tabs component.
 */
export interface Tab {
  /**
   * The label of the tab, which can be either a string or a React node.
   */
  label: string | React.ReactNode
  /**
   * The unique key identifying the tab.
   */
  key: string
  /**
   * The URL for the tab, if applicable. Used for navigation.
   */
  url?: string
  /**
   * A flag to display a "new" tag next to the tab.
   */
  isNew?: boolean
}

/**
 * Props for the Tabs component.
 */
interface TabsProps {
  /**
   * Optional navigation label for accessibility purposes.
   */
  nav?: string
  /**
   * An array of tabs to be rendered.
   */
  tabs: Tab[]
  /**
   * The key of the selected tab.
   */
  selectedKey?: string
  /**
   * Custom CSS class for additional styling of the tabs.
   */
  className?: string
}

/**
 * The Tabs component is used to render a series of tabbed navigation links.
 * It supports icons, "new" indicators, and custom navigation URLs.
 *
 * ---
 * **Important: Always use a unique `key` for each tab to ensure correct rendering and selection behavior.**
 * ---
 *
 * @param {TabsProps} props - The props for the Tabs component.
 * @returns {JSX.Element} The rendered Tabs component.
 *
 * @example
 * <Tabs
 *   tabs={[{
 *     key: 'home',
 *     label: 'Home',
 *     url: '/home',
 *     isNew: true,
 *   }, {
 *     key: 'profile',
 *     label: 'Profile',
 *     url: '/profile',
 *   }]}
 *   selectedKey="home"
 * />
 *
 * @accessibility
 * - **Navigation Label**: Use the `nav` prop to provide an accessible label for the tabs navigation.
 * - **Link Navigation**: Each tab can have a URL to allow for client-side navigation using React Router's `<Link>` component.
 */
export const Tabs = ({
  nav,
  selectedKey,
  tabs,
  className,
}: TabsProps): JSX.Element => {
  const content = (
    <TabsPrimitive.Root
      className={cn(styles['tabs-root'], className)}
      value={selectedKey}
    >
      <TabsPrimitive.List className={styles['tabs']}>
        {tabs.map(({ key, label, url, isNew = false }) => (
          <TabsPrimitive.Trigger
            className={cn(styles['tabs-tab'], {
              [styles['is-selected']]: selectedKey === key,
            })}
            key={key}
            value={key}
            asChild
          >
            <Link to={url ?? '#'} className={styles['tabs-tab-link']}>
              <span className={styles['tabs-tab-label']}>{label}</span>
              {isNew && (
                <Tag
                  className={styles['tabs-tab-new']}
                  variant={TagVariant.BLUE}
                >
                  Nouveau
                </Tag>
              )}
            </Link>
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
    </TabsPrimitive.Root>
  )

  return nav ? <nav aria-label={nav}>{content}</nav> : content
}
