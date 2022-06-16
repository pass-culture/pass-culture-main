import { Layout, LayoutProps } from 'react-admin'

import { CustomAppBar } from './CustomAppBar'
import { Menu } from './CustomMenu'

export const CustomLayout = (props: LayoutProps) => {
  return <Layout {...props} appBar={CustomAppBar} sidebar={Menu} />
}
