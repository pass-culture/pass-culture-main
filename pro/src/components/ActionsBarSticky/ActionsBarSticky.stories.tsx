import type { StoryObj } from '@storybook/react'
import { configureTestStore } from 'commons/store/testUtils'
import { Provider } from 'react-redux'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { ActionsBarSticky } from './ActionsBarSticky'

export default {
  title: 'components/ActionsBarSticky',
  component: ActionBar,
  decorators: [
    (Story: any) => (
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
          <Story />
        </div>
      </div>
    ),
  ],
}

function ActionBar() {
  return (
    <Provider store={configureTestStore({})}>
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
    </Provider>
  )
}

export const Default: StoryObj<typeof ActionBar> = {
  args: {
    size: 'medium',
  },
}
