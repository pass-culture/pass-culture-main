import type { Meta, StoryObj } from '@storybook/react-vite'
import React from 'react'
import { withRouter } from 'storybook-addon-remix-react-router'

import strokeUserProfile from '@/icons/stroke-user.svg'
import strokeOffer from '@/icons/stroke-offer.svg'
import strokeParty from '@/icons/stroke-party.svg'
import { strokeIcons } from '@/ui-kit/Icons/iconsList'

import { InfoPanel } from './InfoPanel'
import { InfoPanelSize, InfoPanelSurface } from './types'

const iconOptions = {
  none: null,
  ...Object.fromEntries(
    strokeIcons.map((icon) => {
      // extract the name of the icon from the path (ex: '@/icons/full-link.svg' -> 'full-link')
      const name = icon.src.split('/').pop()?.replace('.svg', '') || ''
      return [name, icon.src]
    })
  ),
}

/**
 * `InfoPanel` affiche une information contextuelle avec un titre et un texte descriptif.
 *
 * Il supporte deux variantes visuelles (surfaces) :
 * - **Flat** : affiche une icône ou un numéro d'étape à gauche sur un fond plat.
 * - **Elevated** : affiche une icône ou un numéro d'étape dans une carte avec bordure.
 *
 * Chaque surface peut être rendue en deux tailles : `large` (par défaut) et `small`.
 */
const meta: Meta<typeof InfoPanel> = {
  title: '@/ui-kit/InfoPanel',
  component: InfoPanel,
  decorators: [withRouter],
  args: {
    title: 'Panel title',
    children: 'Panel content description.',
    size: InfoPanelSize.LARGE,
  },
  argTypes: {
    surface: {
      control: 'select',
      options: Object.values(InfoPanelSurface),
      description:
        'Variante visuelle. `flat` n\'a pas de bordure, `elevated` a une bordure.',
    },
    size: {
      control: 'select',
      options: Object.values(InfoPanelSize),
      description: 'Taille du panneau.',
      table: {
        defaultValue: {
          summary: 'large',
        },
      }
    },
    title: {
      control: 'text',
      description: 'Titre affiché en haut du panneau.',
    },
    children: {
      control: 'text',
      description: 'Contenu du panneau (chaîne de caractères ou JSX).',
    },
    stepNumber: {
      control: 'number',
      description: "Numéro d'étape affiché à gauche.",
    },
    icon: {
      control: 'select',
      options: Object.keys(iconOptions),
      mapping: iconOptions,
      description: "Source de l'icône SVG affichée à gauche (uniquement quand `stepNumber` est non-défini)",
      if: { arg: 'stepNumber', exists: false },
    },
    iconAlt: {
      control: 'text',
      description: "Texte alternatif accessible pour l'icône (uniquement quand `stepNumber` est non-défini)",
      if: { arg: 'stepNumber', exists: false },
    },
  },
}

export default meta

type Story = StoryObj<typeof InfoPanel>

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
// Stories individuelles — une par variante de surface, interactives
// -----------------------------------------------------------

/**
 * Surface flat avec icône. L'icône et son texte alternatif sont requis.
 */
export const Flat: Story = {
  args: {
    title: '4 millions de jeunes',
    children:
      "Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles",
    surface: InfoPanelSurface.FLAT,
    size: InfoPanelSize.LARGE,
    icon: strokeUserProfile,
    iconAlt: 'Profil utilisateur',
  },
}

/**
 * Surface elevated avec numéro d'étape. La prop `stepNumber` est requise.
 */
export const Elevated: Story = {
  args: {
    title: 'Nos équipes valident votre dossier — 48 heures',
    children:
      'Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi une validation des équipes externes rattachées à Adage.',
    surface: InfoPanelSurface.ELEVATED,
    size: InfoPanelSize.LARGE,
    stepNumber: 1,
  },
}

/**
 * Surface flat en taille small.
 */
export const FlatSmall: Story = {
  args: {
    ...Flat.args,
    size: InfoPanelSize.SMALL,
  },
}

/**
 * Surface elevated en taille small.
 */
export const ElevatedSmall: Story = {
  args: {
    ...Elevated.args,
    size: InfoPanelSize.SMALL,
  },
}

// -----------------------------------------------------------
// Stories catalogue — vues matricielles pour comparaison visuelle
// -----------------------------------------------------------

/**
 * Comparaison côte à côte des panneaux **flat** dans les deux tailles.
 */
export const FlatSizes: Story = {
  render: () => (
    <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Large</h4>
        <InfoPanel
          title="4 millions de jeunes"
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.LARGE}
          icon={strokeUserProfile}
          iconAlt="Profil utilisateur"
        >
          Touchez une audience de 15-21 ans partout en France, activement à la
          recherche d'expériences culturelles
        </InfoPanel>
      </div>
      <div style={columnStyles}>
        <h4>Small</h4>
        <InfoPanel
          title="4 millions de jeunes"
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.SMALL}
          icon={strokeUserProfile}
          iconAlt="Profil utilisateur"
        >
          Touchez une audience de 15-21 ans partout en France, activement à la
          recherche d'expériences culturelles
        </InfoPanel>
      </div>
    </div>
  ),
}

/**
 * Comparaison côte à côte des panneaux **elevated** dans les deux tailles.
 */
export const ElevatedSizes: Story = {
  render: () => (
    <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Large</h4>
        <InfoPanel
          title="Nos équipes valident votre dossier — 48 heures"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.LARGE}
          stepNumber={1}
        >
          Elles peuvent demander des documents complémentaires. Les offres
          scolaires nécessitent aussi une validation des équipes externes
          rattachées à Adage.
        </InfoPanel>
      </div>
      <div style={columnStyles}>
        <h4>Small</h4>
        <InfoPanel
          title="Nos équipes valident votre dossier — 48 heures"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          stepNumber={1}
        >
          Elles peuvent demander des documents complémentaires. Les offres
          scolaires nécessitent aussi une validation des équipes externes
          rattachées à Adage.
        </InfoPanel>
      </div>
    </div>
  ),
}

/**
 * Plusieurs panneaux (flat ou elevated) utilisés comme liste d'étapes numérotées.
 */
export const StepList: Story = {
  render: () => (
    <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Flat Small</h4>
        <div style={{ ...columnStyles, gap: '32px' }}>
          <InfoPanel
            title="Décrivez votre structure et votre activité culturelle - 5 minutes"
            surface={InfoPanelSurface.FLAT}
            size={InfoPanelSize.SMALL}
            stepNumber={1}
          >
            Renseignez les informations administratives et les domaines dans lesquels vous intervenez
          </InfoPanel>
          <InfoPanel
            title="Nos équipes valident votre dossier — 48 heures"
            surface={InfoPanelSurface.FLAT}
            size={InfoPanelSize.SMALL}
            stepNumber={2}
          >
            Elles peuvent demander des documents complémentaires. Les offres
            scolaires nécessitent aussi une validation des équipes externes
            rattachées à Adage.
          </InfoPanel>
          <InfoPanel
            title="Créez vos premières offres - 3 minutes"
            surface={InfoPanelSurface.FLAT}
            size={InfoPanelSize.SMALL}
            stepNumber={3}
          >
            Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.
          </InfoPanel>
        </div>
      </div>
      <div style={columnStyles}>
        <h4>Elevated Small</h4>
        <InfoPanel
          title="Décrivez votre structure et votre activité culturelle - 5 minutes"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          stepNumber={1}
        >
          Renseignez les informations administratives et les domaines dans lesquels vous intervenez
        </InfoPanel>
        <InfoPanel
          title="Nos équipes valident votre dossier — 48 heures"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          stepNumber={2}
        >
          Elles peuvent demander des documents complémentaires. Les offres
          scolaires nécessitent aussi une validation des équipes externes
          rattachées à Adage.
        </InfoPanel>
        <InfoPanel
          title="Créez vos premières offres - 3 minutes"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          stepNumber={3}
        >
          Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.
        </InfoPanel>
      </div>
    </div>
  ),
}

/**
 * Plusieurs panneaux (flat ou elevated) utilisés avec des icônes.
 */
export const IconsList: Story = {
  render: () => (
    <div style={rowStyles}>
      <div style={columnStyles}>
        <h4>Flat Small</h4>
        <div style={{ ...columnStyles, gap: '32px' }}>
          <InfoPanel
            title="4 millions de jeunes"
            surface={InfoPanelSurface.FLAT}
            size={InfoPanelSize.SMALL}
            icon={strokeUserProfile}
            iconAlt="Profil utilisateur"
          >
            Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles
          </InfoPanel>
          <InfoPanel
            title="Une inscription simple et rapide"
            surface={InfoPanelSurface.FLAT}
            size={InfoPanelSize.SMALL}
            icon={strokeOffer}
            iconAlt="Profil utilisateur"
          >
            Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée
          </InfoPanel>
          <InfoPanel
            title="Publiez quand vous voulez"
            surface={InfoPanelSurface.FLAT}
            size={InfoPanelSize.SMALL}
            icon={strokeParty}
            iconAlt="Profil utilisateur"
          >
            Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année
          </InfoPanel>
        </div>
      </div>
      <div style={columnStyles}>
        <h4>Elevated Small</h4>
        <InfoPanel
          title="4 millions de jeunes"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          icon={strokeOffer}
          iconAlt="Profil utilisateur"
        >
          Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles
        </InfoPanel>
        <InfoPanel
          title="Une inscription simple et rapide"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          icon={strokeUserProfile}
          iconAlt="Profil utilisateur"
        >
          Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée
        </InfoPanel>
        <InfoPanel
          title="Publiez quand vous voulez"
          surface={InfoPanelSurface.ELEVATED}
          size={InfoPanelSize.SMALL}
          icon={strokeParty}
          iconAlt="Profil utilisateur"
        >
          Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année
        </InfoPanel>
      </div>
    </div>
  ),
}
