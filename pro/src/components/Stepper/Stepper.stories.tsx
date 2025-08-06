import type { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Step, Stepper } from './Stepper'

export default {
  title: '@/components/Stepper',
  component: Stepper,
  decorators: [withRouter],
}

const stepList: Step[] = [
  {
    id: '1',
    label: 'Informations',
    url: '/informations',
  },
  {
    id: '2',
    label: 'Stock & Prix',
    url: '/stocks',
  },
  {
    id: '3',
    label: 'Récapitulatif',
    url: '/recapitulatif',
  },
  {
    id: '4',
    label: 'Confirmation',
  },
  {
    id: '5',
    label: 'Encore un élément',
  },
  {
    id: '6',
    label: 'Final',
  },
]

export const Default: StoryObj<typeof Stepper> = {
  args: {
    activeStep: '3',
    steps: stepList,
  },
}
