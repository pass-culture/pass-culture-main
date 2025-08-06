import type { StoryObj } from '@storybook/react'

import fullTrashIcon from '@/icons/full-trash.svg'

import { ListIconButton } from './ListIconButton'

export default {
  title: '@/ui-kit/ListIconButton',
  component: ListIconButton,
  decorators: [
    (Story: any) => (
      <div style={{ margin: '50px', display: 'flex' }}>
        <Story />
      </div>
    ),
  ],
}

export const Default: StoryObj<typeof ListIconButton> = {
  args: {
    icon: fullTrashIcon,
    tooltipContent: <>Duplicate</>,
  },
}

export const Link: StoryObj<typeof ListIconButton> = {
  args: {
    icon: fullTrashIcon,
    tooltipContent: <>Lire la FAQ</>,
    url: 'http://wwww.test.com',
    onClick: () => {},
    isExternal: true,
  },
}
