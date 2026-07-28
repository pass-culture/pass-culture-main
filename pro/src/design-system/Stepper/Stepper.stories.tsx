import type { Meta, StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'

import type { StepItem } from './Stepper'
import { Stepper } from './Stepper'
import { noop } from '@/commons/utils/noop'

const meta: Meta<typeof Stepper> = {
  title: '@/design-system/Stepper',
  component: Stepper,
  decorators: [withRouter],
}

export default meta
type Story = StoryObj<typeof Stepper>

const mockStepsSimple: StepItem[] = [
  { id: 'category', label: 'Choisissez votre catégorie', onClick: noop },
  { id: 'pricing', label: 'Définissez un tarif', onClick: noop },
  { id: 'validation', label: 'Validez votre offre', onClick: noop },
]

const mockStepsDetailed: StepItem[] = [
  {
    id: 'category',
    label: 'Choisissez votre catégorie',
    sublabel: 'Sélectionnez le type d’offre',
    onClick: noop,
  },
  {
    id: 'pricing',
    label: 'Définissez un tarif',
    sublabel: 'Saisissez les informations de prix',
    onClick: noop,
  },
  {
    id: 'validation',
    label: 'Validez votre offre',
    sublabel: 'Confirmez et publiez',
    onClick: noop,
  },
]

export const HorizontalSimple: Story = {
  args: {
    steps: mockStepsSimple,
    activeStep: 'pricing',
    orientation: 'horizontal',
  },
}

export const HorizontalDetailed: Story = {
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'horizontal',
  },
}

export const VerticalSimple: Story = {
  args: {
    steps: mockStepsSimple,
    activeStep: 'pricing',
    orientation: 'vertical',
  },
}

export const VerticalDetailed: Story = {
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'vertical',
  },
}

export const WithNavigationLinks: Story = {
  args: {
    steps: [
      {
        id: 'category',
        label: 'Choisissez votre catégorie',
        sublabel: 'Lien vers /category',
        url: '/category',
        onClick: noop,
      },
      {
        id: 'pricing',
        label: 'Définissez un tarif',
        sublabel: 'Lien vers /pricing',
        url: '/pricing',
        onClick: noop,
      },
      {
        id: 'summary',
        label: 'Relisez votre offre',
        sublabel: 'Étape en cours : pas de lien vers soi-même',
        url: '/summary',
      },
      {
        id: 'validation',
        label: 'Validez votre offre',
        sublabel: 'À venir : lien inactif',
        url: '/validation',
      },
    ],
    activeStep: 'summary',
    orientation: 'horizontal',
  },
}

export const AutoResponsive: Story = {
  render: (args) => (
    <div
      style={{
        width: '100%',
        resize: 'horizontal',
        overflow: 'auto',
        border: '1px dashed #ccc',
        padding: '1rem',
      }}
    >
      <p style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: '#666' }}>
        Redimensionnez ce bloc pour voir le composant basculer d’horizontal à
        vertical (seuil : 80px par étape).
      </p>
      <Stepper {...args} />
    </div>
  ),
  args: {
    steps: mockStepsDetailed,
    activeStep: 'pricing',
    orientation: 'auto',
  },
}

export const AllStatesShowcase: Story = {
  args: {
    steps: [
      {
        id: 'done',
        label: 'Étape 1 terminée',
        sublabel: 'Cliquable et validée',
        onClick: () => alert('Clic Étape 1'),
      },
      {
        id: 'current',
        label: 'Étape 2 active',
        sublabel: 'C’est l’étape en cours (non cliquable)',
        onClick: () => alert('Clic Étape 2'),
      },
      {
        id: 'upcoming',
        label: 'Étape 3 à venir',
        sublabel: 'Pas encore atteignable',
        onClick: noop,
      },
      {
        id: 'last',
        label: 'Étape 4 dernière',
        sublabel: 'Dernière étape',
        onClick: noop,
      },
    ],
    activeStep: 'current'
  },
}
