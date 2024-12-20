import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { MultiSelect } from './MultiSelect'

export default {
  title: 'ui-kit/MultiSelect',
  decorators: [withRouter],
  component: MultiSelect,
  parameters: {
    docs: {
      story: {
        inline: false,
        iframeHeight: 380,
      },
    },
  },
}

const defaultOptions = [
  { id: '1', label: '78 - Yvelines' },
  { id: '2', label: '75 - Paris' },
  { id: '3', label: '44 - Nantes' },
  { id: '4', label: '76 - Rouen' },
  { id: '5', label: '77 - Seine et Marne' },
]

const defaultProps = {
  options: defaultOptions,
  legend: 'Département',
  label: 'Selectionner un département',
}

export const Default: StoryObj<typeof MultiSelect> = {
  args: {
    ...defaultProps,
  },
}

export const WithDefaultOptions: StoryObj<typeof MultiSelect> = {
  args: {
    ...defaultProps,
    defaultOptions: [
      { id: '2', label: '75 - Paris' },
      { id: '3', label: '44 - Nantes' },
    ],
  },
}

export const WithSearchInput: StoryObj<typeof MultiSelect> = {
  args: {
    ...defaultProps,
    hasSearch: true,
    searchExample: 'Ex : 44 - Nantes',
    searchLabel: 'Rechercher des départements',
    legend: 'Départements',
    label: 'Selectionner des départements',
  },
}
