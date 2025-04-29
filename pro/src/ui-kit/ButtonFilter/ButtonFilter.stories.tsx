import type { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { ButtonFilter } from './ButtonFilter'

export default {
  title: 'ui-kit/ButtonFilter',
  decorators: [
    withRouter,
    (Story: any) => (
      <div style={{ margin: '50px', display: 'flex' }}>
        <Story />
      </div>
    ),
  ],
  argTypes: {
    isOpen: {
      control: 'boolean', // control type for the boolean prop
      defaultValue: true,
    },
    isActive: {
      control: 'boolean', // control type for the boolean prop
      defaultValue: false,
    },
    children: {
      control: 'text', // control type for the text children prop
      defaultValue: 'Filter Button', // default label
    },
    testId: {
      control: 'text', // optional control for testing purposes
      defaultValue: 'button-filter', // default test ID
    },
  },
  component: ButtonFilter,
}

export const DefaultButton: StoryObj<typeof ButtonFilter> = {
  args: {
    isOpen: false,
    isActive: false,
    children: 'Filter Button',
  },
}

export const OpenButton: StoryObj<typeof ButtonFilter> = {
  args: {
    isOpen: true,
    isActive: false,
    children: 'Open Filter',
  },
}

export const ActiveButton: StoryObj<typeof ButtonFilter> = {
  args: {
    isOpen: false,
    isActive: true,
    children: 'Active Filter',
  },
}
