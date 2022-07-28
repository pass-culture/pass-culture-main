import type { Story } from '@storybook/react'
import React from 'react'

import { IBoxRoundedProps } from './BoxRounded'

import { BoxRounded } from '.'

export default {
  title: 'ui-kit/BoxRounded',
}

const Template: Story<IBoxRoundedProps> = args => <BoxRounded {...args} />

export const DefaultBoxRounded = Template.bind({})

DefaultBoxRounded.args = {
  children: (
    <div>
      <h1>Test title</h1>
      <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
        commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
        velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
        occaecat cupidatat non proident, sunt in culpa qui officia deserunt
        mollit anim id est laborum.
      </p>
    </div>
  ),
  onClickModify: () => alert('Modify button have been clicked.'),
}
