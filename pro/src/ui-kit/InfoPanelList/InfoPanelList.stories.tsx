import type { Meta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import { withRouter } from 'storybook-addon-remix-react-router'

import strokeOffer from '@/icons/stroke-offer.svg'
import strokeParty from '@/icons/stroke-party.svg'
import strokeUserProfile from '@/icons/stroke-user.svg'

import { InfoPanelList } from './InfoPanelList'
import { InfoPanelSurface, InfoPanelSize, InfoPanelVariant } from './types'

const UNORDERED_PANELS_MOCK = [
  {
    title: '4 millions de jeunes',
    description:
      "Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles.",
    icon: strokeUserProfile,
    iconAlt: 'Profil utilisateur',
  },
  {
    title: 'Une inscription simple et rapide',
    description:
      "Contrairement aux appels à projets lourds, l'inscription est simple et guidée.",
    icon: strokeOffer,
    iconAlt: 'Offre culturelle',
  },
  {
    title: 'Publiez quand vous voulez',
    description:
      "Créez et modifiez vos offres, qu'elles soient gratuites ou payantes, à tout moment de l'année.",
    icon: strokeParty,
    iconAlt: 'Événement',
  },
]

const ORDERED_PANELS_MOCK = [
  {
    title: 'Décrivez votre structure et votre activité culturelle',
    description:
      'Renseignez les informations administratives et les domaines dans lesquels vous intervenez.',
  },
  {
    title: 'Nos équipes valident votre dossier — 48 heures',
    description:
      'Elles peuvent demander des documents complémentaires si nécessaire.',
  },
  {
    title: 'Créez vos premières offres',
    description:
      "Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application.",
  },
]

/**
 * `InfoPanelList` affiche une liste de panneaux d'information (`InfoPanel`).
 *
 * Le composant gère deux formes via une union discriminée :
 * - **UNORDERED** : rendus sous forme de liste à puces (`<ul>`), chaque item contient obligatoirement une icône.
 * - **ORDERED** : rendus sous forme de liste ordonnée (`<ol>`), chaque item est automatiquement numéroté (sans icône).
 */
const meta: Meta<typeof InfoPanelList> = {
  title: '@/ui-kit/InfoPanelList',
  component: InfoPanelList,
  decorators: [withRouter],
  args: {
    surface: InfoPanelSurface.FLAT,
    size: InfoPanelSize.LARGE,
    titleLevel: '3',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: Object.values(InfoPanelVariant),
      description:
        'Variante de la liste. `unordered` (`<ul>`) impose des icônes, `ordered` (`<ol>`) génère les numéros d\'étapes.',
    },
    surface: {
      control: 'select',
      options: Object.values(InfoPanelSurface),
      description:
        'Variante visuelle. `flat` n\'a pas de bordure, `elevated` ajoute un conteneur avec bordure.',
    },
    size: {
      control: 'select',
      options: Object.values(InfoPanelSize),
      description: 'Taille des panneaux dans la liste.',
      table: {
        defaultValue: { summary: 'large' },
      },
    },
    titleLevel: {
      control: 'radio',
      options: ['2', '3'],
      description: 'Niveau du titre HTML généré (`<h2>` ou `<h3>`).',
      table: {
        defaultValue: { summary: '3' },
      },
    },
    panels: {
      control: 'object',
      description: 'Tableau des panneaux à afficher.',
    },
  },
}

export default meta

type Story = StoryObj<typeof InfoPanelList>

const rowStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'row',
  gap: '24px',
  alignItems: 'flex-start',
}

const columnStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
  flex: 1,
}

// -----------------------------------------------------------
// Stories individuelles interactives
// -----------------------------------------------------------

/**
 * Liste non ordonnée avec icônes obligatoires sur fond plat (`flat`).
 */
export const UnorderedFlat: Story = {
  args: {
    variant: InfoPanelVariant.UNORDERED,
    surface: InfoPanelSurface.FLAT,
    size: InfoPanelSize.LARGE,
    panels: UNORDERED_PANELS_MOCK,
  },
}

/**
 * Liste ordonnée avec numérotation automatique en cartes `elevated`.
 */
export const OrderedElevated: Story = {
  args: {
    variant: InfoPanelVariant.ORDERED,
    surface: InfoPanelSurface.ELEVATED,
    size: InfoPanelSize.LARGE,
    panels: ORDERED_PANELS_MOCK,
  },
}

// -----------------------------------------------------------
// Stories catalogue / vues matricielles
// -----------------------------------------------------------

/**
 * Comparaison côte à côte des variantes d'affichage pour une liste d'étapes (`ORDERED`).
 */
export const OrderedComparison: Story = {
  render: () => (
    <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Flat - Large</h4>
        <InfoPanelList
          variant={InfoPanelVariant.ORDERED}
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.LARGE}
          panels={ORDERED_PANELS_MOCK}
        />
      </div>
      <div style={columnStyles}>
        <h4>Elevated - Small</h4>
        <InfoPanelList
          variant={InfoPanelVariant.ORDERED}
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          panels={ORDERED_PANELS_MOCK}
        />
      </div>
    </div>
  ),
}

/**
 * Comparaison côte à côte des variantes d'affichage pour une liste à icônes (`UNORDERED`).
 */
export const UnorderedComparison: Story = {
  render: () => (
    <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Flat - Small</h4>
        <InfoPanelList
          variant={InfoPanelVariant.UNORDERED}
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.SMALL}
          panels={UNORDERED_PANELS_MOCK}
        />
      </div>
      <div style={columnStyles}>
        <h4>Elevated - Large</h4>
        <InfoPanelList
          variant={InfoPanelVariant.UNORDERED}
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.LARGE}
          panels={UNORDERED_PANELS_MOCK}
        />
      </div>
    </div>
  ),
}
