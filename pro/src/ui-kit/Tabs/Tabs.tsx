import { type NavLinkItem, NavLinkItems } from './NavLinkItems/NavLinkItems'
import { type TabItem, TabItems } from './TabItems/TabItems'

export type BaseTabsProps = {
  /**
   * Navigation accessible name
   */
  navLabel: string
  /**
   * The key of the selected link.
   */
  selectedKey?: string
  className?: string
}

type StandardTabsProps = BaseTabsProps & {
  type: 'tabs'
  /**
   * An array of links or tabs to be rendered.
   */
  items: TabItem[]
  /**
   * The function called when a tab is clicked
   */
  onChange: (selectedKey: string) => void
}

type NavTabsProps = BaseTabsProps & {
  type: 'links'
  /**
   * An array of links or tabs to be rendered.
   */
  items: NavLinkItem[]
}

/**
 * The Tabs component is used to render tabs. It will renders two kind of DOM depending on the requested `type`
 *  - a list of navigation links
 *  - a list of tab buttons
 *
 * @example
 * <Tabs
 *   type="links"
 *   items={[{
 *     key: 'home',
 *     label: 'Home',
 *     url: '/home',
 *   }, {
 *     key: 'profile',
 *     label: 'Profile',
 *     url: '/profile',
 *   }]}
 *   selectedKey="home"
 * />
 */
export const Tabs = (props: StandardTabsProps | NavTabsProps): JSX.Element => {
  return props.type === 'tabs' ? (
    <TabItems
      navLabel={props.navLabel}
      selectedKey={props.selectedKey}
      tabs={props.items}
      onChange={props.onChange}
      className={props.className}
    />
  ) : (
    <NavLinkItems
      navLabel={props.navLabel}
      selectedKey={props.selectedKey}
      links={props.items}
      className={props.className}
    />
  )
}
