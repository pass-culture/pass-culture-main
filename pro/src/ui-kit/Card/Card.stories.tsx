import type { StoryObj } from '@storybook/react-vite'
import image from './assets/sample-image-landscape.jpg'

import { Card } from './Card'
import { Button } from '../Button/Button'

export default {
  title: '@/ui-kit/Card',
  component: Card,
}

export const Default: StoryObj<typeof Card> = {
  args: {
    imageSrc: image,
    title: <h3>"Ma carte"</h3>,
    actions: <Button>Do it !</Button>,
    children: 'Hello world',
  },
}

