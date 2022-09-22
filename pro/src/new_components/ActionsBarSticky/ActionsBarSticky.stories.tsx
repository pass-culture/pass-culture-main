import type { ComponentStory } from '@storybook/react'
import React from 'react'

import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import ActionsBarSticky from './ActionsBarSticky'

export default {
  title: 'components/ActionsBarSticky',
  component: ActionsBarSticky,
}

const Left = (): JSX.Element => <Button>Bouton Gauche</Button>

const Right = (): JSX.Element => (
  <>
    <Button>Bouton Droite</Button>
    <Button>Autre bouton</Button>
    <Button variant={ButtonVariant.SECONDARY}>Encore un</Button>
  </>
)

const Template: ComponentStory<typeof ActionsBarSticky> = args => (
  <div
    style={{
      width: '874px',
      height: '1500px',
      backgroundColor: 'lightblue',
      margin: 'auto',
    }}
  >
    <ActionsBarSticky {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  isVisible: true,
  left: <Left />,
  right: <Right />,
}
