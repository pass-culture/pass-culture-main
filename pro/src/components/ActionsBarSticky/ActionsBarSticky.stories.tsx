import type { StoryObj } from '@storybook/react-vite'
import { Provider } from 'react-redux'

import { configureTestStore } from '@/commons/store/testUtils'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import { ActionsBarSticky } from './ActionsBarSticky'

export default {
  title: '@/components/ActionsBarSticky',
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
          <Button label="Bouton Gauche" />
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <Button label="Bouton Droite" />
          <Button label="Autre bouton" />
          <Button variant={ButtonVariant.SECONDARY} label="Encore un" />
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
