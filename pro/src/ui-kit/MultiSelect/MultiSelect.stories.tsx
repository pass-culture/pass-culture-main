import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { MultiSelect } from './MultiSelect'

export default {
  title: '@/ui-kit/MultiSelect',
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
  { id: '1', label: '01 - Ain' },
  { id: '2', label: '02 - Aisne' },
  { id: '3', label: '03 - Allier' },
  { id: '4', label: '04 - Alpes-de-Haute-Provence' },
  { id: '5', label: '05 - Hautes-Alpes' },
  { id: '6', label: '06 - Alpes-Maritimes' },
  { id: '7', label: '07 - Ardèche' },
  { id: '8', label: '08 - Ardennes' },
  { id: '9', label: '09 - Ariège' },
  { id: '10', label: '10 - Aube' },
  { id: '11', label: '11 - Aude' },
  { id: '12', label: '12 - Aveyron' },
  { id: '13', label: '13 - Bouches-du-Rhône' },
  { id: '14', label: '14 - Calvados' },
  { id: '15', label: '15 - Cantal' },
]

const defaultProps = {
  options: defaultOptions,
  label: 'Sélectionner un département',
  onSelectedOptionsChanged: () => {},
  buttonLabel: 'Départements',
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
    searchLabel: 'Rechercher des départements',
    buttonLabel: 'Départements',
    label: 'Sélectionner des départements',
    name: 'départements',
  },
}

export const WithSelectAllOption: StoryObj<typeof MultiSelect> = {
  args: {
    ...defaultProps,
    hasSelectAllOptions: true,
    buttonLabel: 'Départements',
    label: 'Sélectionner des départements',
    name: 'départements',
  },
}

export const WithSearchInputAndSelectAllOption: StoryObj<typeof MultiSelect> = {
  args: {
    ...defaultProps,
    hasSearch: true,
    searchLabel: 'Rechercher des départements',
    hasSelectAllOptions: true,
    buttonLabel: 'Départements',
    label: 'Sélectionner des départements',
  },
}

export const WithError: StoryObj<typeof MultiSelect> = {
  args: {
    ...defaultProps,
    buttonLabel: 'Départements',
    label: 'Sélectionner des départements',
    error: 'Veuillez sélectionner un département',
    onBlur: () => {},
    name: 'départements',
  },
}
