import type { StoryObj } from '@storybook/react'
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

export const Tab: StoryObj<typeof Breadcrumb> = {
  args: {
    activeStep: '3',
    steps: stepList,
    isDisabled: false,
    styleType: BreadcrumbStyle.TAB,
  },
}

export const Stepper: StoryObj<typeof Breadcrumb> = {
  args: {
    activeStep: '3',
    steps: stepList,
    isDisabled: false,
    styleType: BreadcrumbStyle.STEPPER,
  },
}
