import type { StoryObj } from '@storybook/react-vite'
import image from './assets/sample-image-landscape.jpg'

import { Button } from '@/design-system/Button/Button'
import { Card } from './Card'

export default {
  title: '@/ui-kit/Card',
  component: Card,
}

export const Default: StoryObj<typeof Card> = {
  args: {
    imageSrc: image,
    title: <h3>"Ma carte"</h3>,
    actions: <Button label='Do it !'></Button>,
    children: 'Hello world',
  },
}

