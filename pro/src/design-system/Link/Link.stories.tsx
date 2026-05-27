import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { useLocation } from 'react-router'

import {
  reactRouterParameters,
  withRouter,
} from 'storybook-addon-remix-react-router'
import fullLinkIcon from '@/icons/full-link.svg'
import fullNextIcon from '@/icons/full-next.svg'
import fullRightIcon from '@/icons/full-right.svg'
import { Link } from './Link'
import { type LinkProps, LinkColor, LinkSize } from './types'

const iconOptions = {
  none: undefined,
  'full-link': fullLinkIcon,
  'full-next': fullNextIcon,
  'full-right': fullRightIcon,
}

const InfoBadge = ({
  children,
}: {
  children: React.ReactNode
}) => {
  return (
    <div
      style={{
        marginBottom: '1rem',
        padding: '0.5rem 0.75rem',
        background: '#f4f4f5',
        border: '1px solid #e4e4e7',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '0.875rem',
        color: '#52525b',
      }}
    >
      {children}
    </div>
  )
}

const LinkWithPathname = (args: LinkProps) => {
  const { pathname } = useLocation()

  return (
    <>
      <InfoBadge>
        Pathname courant : <strong>{pathname}</strong>
      </InfoBadge>
      <Link {...args} />
    </>
  )
}

const LinkWithOnClickCounter = (args: LinkProps) => {
  const [clickCount, setClickCount] = useState(0)

  return (
    <>
      <InfoBadge>
        onClick called <strong>{clickCount}</strong> time
        {clickCount === 1 ? '' : 's'}
      </InfoBadge>
      <Link {...args} onClick={() => setClickCount((count) => count + 1)} />
    </>
  )
}

const meta: Meta<typeof Link> = {
  title: '@/design-system/Link',
  component: Link,
  decorators: [withRouter],
  parameters: {
    reactRouter: reactRouterParameters({
      routing: { path: '*', useStoryElement: true },
    }),
  },
  render: (args) => <Link {...args} />,
  args: {
    label: 'Label explicite du lien',
    to: '/default',
    icon: iconOptions.none,
    size: LinkSize.DEFAULT,
    color: LinkColor.BRAND,
    isExternalLink: false,
    shouldOpenNewTab: false,
  },
  argTypes: {
    label: { control: 'text' },
    to: { control: 'text' },
    icon: {
      control: 'select',
      options: Object.keys(iconOptions),
      mapping: iconOptions,
    },
    size: {
      control: 'select',
      options: Object.values(LinkSize),
    },
    color: {
      control: 'select',
      options: Object.values(LinkColor),
    },
    isExternalLink: { control: 'boolean' },
    shouldOpenNewTab: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Link>

export const Default: Story = {
  render: (args) => <LinkWithPathname {...args} />,
}

export const Small: Story = {
  args: { size: LinkSize.SMALL, to: '/small' },
}

export const ExtraSmall: Story = {
  args: { size: LinkSize.EXTRA_SMALL, to: '/extra-small' },
}

export const Neutral: Story = {
  args: { color: LinkColor.NEUTRAL, to: '/neutral' },
}

export const WithIcon: Story = {
  args: { icon: fullNextIcon, to: '/with-icon' },
}

export const InNewTab: Story = {
  args: { shouldOpenNewTab: true, to: '/in-new-tab' },
}

export const External: Story = {
  args: {
    to: 'https://pass-culture.github.io/pass-culture-main/?path=/story/design-system-link--external',
    isExternalLink: true,
    shouldOpenNewTab: true,
  },
}

export const WithOnClick: Story = {
  render: (args) => <LinkWithOnClickCounter {...args} />,
  args: {
    to: '/with-on-click',
  },
}
