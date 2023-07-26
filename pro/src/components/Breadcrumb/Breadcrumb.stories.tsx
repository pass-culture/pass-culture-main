import type { ComponentStory } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import type { Step } from 'components/Breadcrumb'

import Breadcrumb, { BreadcrumbStyle } from './Breadcrumb'

export default {
  title: 'components/BreadCrumb',
  component: Breadcrumb,
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

const Template: ComponentStory<typeof Breadcrumb> = args => (
  <div style={{ width: 874 }}>
    <Breadcrumb {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  activeStep: '3',
  steps: stepList,
  isDisabled: false,
  styleType: BreadcrumbStyle.DEFAULT,
}

export const Tab = Template.bind({})

Tab.args = {
  activeStep: '3',
  steps: stepList,
  isDisabled: false,
  styleType: BreadcrumbStyle.TAB,
}

export const Stepper = Template.bind({})

Stepper.args = {
  activeStep: '3',
  steps: stepList,
  isDisabled: false,
  styleType: BreadcrumbStyle.STEPPER,
}
