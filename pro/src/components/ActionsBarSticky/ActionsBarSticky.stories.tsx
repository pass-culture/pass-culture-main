import type { ComponentStory } from '@storybook/react'
import React from 'react'

import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import ActionsBarSticky from './ActionsBarSticky'

export default {
  title: 'components/ActionsBarSticky',
  component: ActionsBarSticky,
}

const Template: ComponentStory<typeof ActionsBarSticky> = () => (
  <div
    style={{
      position: 'fixed',
      left: '0',
      right: '0',
    }}
  >
    <div
      style={{
        width: '874px',
        height: '1500px',
        backgroundColor: 'lightblue',
        margin: 'auto',
      }}
    >
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button>Bouton Gauche</Button>
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <Button>Bouton Droite</Button>
          <Button>Autre bouton</Button>
          <Button variant={ButtonVariant.SECONDARY}>Encore un</Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </div>
  </div>
)

export const Default = Template.bind({})

Default.args = {}
