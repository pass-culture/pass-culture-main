import type { StoryObj } from '@storybook/react'

import strokeProfIcon from 'icons/stroke-prof.svg'

import { RadioButtonWithImage } from './RadioButtonWithImage'

export default {
  title: 'ui-kit/RadioButtonWithImage',
  component: RadioButtonWithImage,
  decorators: [
    (Story: any) => (
      <div style={{ maxWidth: '300px' }}>
        <Story />
      </div>
    ),
  ],
}

const defaultProps = {
  name: 'offerType',
  label: 'Offre Collective',
  icon: strokeProfIcon,
  value: 'collective',
}

export const Default: StoryObj<typeof RadioButtonWithImage> = {
  args: {
    ...defaultProps,
  },
}

export const WithDescription: StoryObj<typeof RadioButtonWithImage> = {
  args: {
    ...defaultProps,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
  },
}
