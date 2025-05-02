import type { StoryObj } from '@storybook/react'

import { AdageMultiselect } from './AdageMultiselect'

export default {
  title: 'ui-kit/formsV2/AdageMultiselect',
  component: AdageMultiselect,
}

const options = [
  { value: 1, label: 'Architecture' },
  { value: 2, label: 'Arts du cirque et arts de la rue' },
  { value: 3, label: 'Gastronomie et arts du goût' },
  { value: 4, label: 'Arts numériques' },
  { value: 5, label: 'Arts visuels, arts plastiques, arts appliqués' },
  { value: 6, label: 'Cinéma, audiovisuel' },
  { value: 7, label: 'Culture scientifique, technique et industrielle' },
  { value: 8, label: 'Danse' },
  { value: 9, label: 'Design' },
  { value: 10, label: 'Développement durable' },
  { value: 11, label: 'Univers du livre, de la lecture et des écritures' },
  { value: 12, label: 'Musique' },
  { value: 13, label: 'Mémoire' },
  { value: 14, label: 'Photographie' },
  { value: 15, label: 'Théâtre, expression dramatique, marionnettes' },
  { value: 16, label: 'Bande dessinée' },
  { value: 17, label: 'Média et information' },
  { value: 18, label: 'Patrimoine' },
]

export const Default: StoryObj<typeof AdageMultiselect> = {
  args: {
    options,
    name: 'educationalDomains',
    label: 'Rechercher un domaine artistique',
    isOpen: true,
    selectedOptions: [],
    onSelectedOptionsChanged: (selectedOptions) => {
      return selectedOptions
    },
  },
}
