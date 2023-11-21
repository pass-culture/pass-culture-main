import type { ComponentStory } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import { Step } from './Stepper'

import Stepper from '.'

export default {
  title: 'components/Stepper',
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

const Template: ComponentStory<typeof Stepper> = (args) => (
  <div style={{ width: 874 }}>
    <Stepper {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  activeStep: '3',
  steps: stepList,
}
