import type { StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'


import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { DropdownButton } from './DropdownButton'

export default {
  title: '@/ui-kit/DropdownButton',
  component: DropdownButton,
  decorators: [withRouter],
}

export const Default: StoryObj<typeof DropdownButton> = {
  args: {
    name: 'Cliquez ici',
    options: [
      {
        id: '1',
        element: <Button variant={ButtonVariant.TERTIARY}>Option 1</Button>,
      },
      {
        id: '2',
        element: <Button variant={ButtonVariant.TERTIARY}>Option 2</Button>,
      },
    ],
  },
}
