import type { StoryObj } from '@storybook/react-vite'
import { useRef, useState } from 'react'
import { withRouter } from 'storybook-addon-remix-react-router'

import fullClearIcon from '@/icons/full-clear.svg'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullDuplicateIcon from '@/icons/full-duplicate.svg'
import fullEditIcon from '@/icons/full-edit.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import fullLogoutIcon from '@/icons/full-logout.svg'
import fullPauseIcon from '@/icons/full-pause.svg'
import fullPlusIcon from '@/icons/full-plus.svg'
import fullShowIcon from '@/icons/full-show.svg'
import fullStarIcon from '@/icons/full-star.svg'
import fullThreeDotsIcon from '@/icons/full-three-dots.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import fullUpIcon from '@/icons/full-up.svg'

import { Button } from '../Button/Button'
import { ButtonVariant, IconPositionEnum } from '../Button/types'
import { TagVariant } from '../Tag/Tag'
import { DropDownItemVariant, Dropdown, type DropdownProps } from './Dropdown'

export default {
  title: '@/design-system/Dropdown',
  decorators: [withRouter],
  component: Dropdown,
  argTypes: {
    label: { control: 'text' },
    align: { control: 'select', options: ['start', 'center', 'end'] },
    items: { control: 'object' },
    width: { control: 'select', options: ['auto', 'trigger', 650] },
  },
}

const DEFAULT_ARGS = {
  label: 'Dropdown',
  align: 'start',
  items: [
    [
      { text: 'Ajouter', icon: fullPlusIcon },
      { text: 'Modifier', icon: fullEditIcon },
      {
        text: 'Supprimer',
        icon: fullTrashIcon,
        variant: DropDownItemVariant.DESTRUCTIVE,
      },
    ],
  ],
  width: 'auto',
} satisfies DropdownProps

export const Default: StoryObj<typeof Dropdown> = {
  args: {
    label: 'Dropdown',
    align: 'start',
    items: [
      [
        {
          text: 'Mettre à la une',
          icon: fullStarIcon,
          tag: {
            label: 'Nouveau',
            variant: TagVariant.CINECLUB,
          },
        },
      ],
      [
        {
          text: 'Un texte super mega long et désactivé',
          icon: fullShowIcon,
          disabled: true,
        },
        {
          text: 'Aller sur Google',
          icon: fullLinkIcon,
          link: {
            target: '_blank',
            to: '//google.fr',
          },
        },
        { text: 'Dupliquer', icon: fullDuplicateIcon },
      ],
      [
        {
          text: 'Supprimer',
          icon: fullTrashIcon,
          variant: DropDownItemVariant.DESTRUCTIVE,
        },
      ],
    ],
  },
}

export const WithIcons: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    items: [
      [
        { text: 'Ajouter', icon: fullPlusIcon },
        { text: 'Modifier', icon: fullEditIcon },
        {
          text: 'Supprimer',
          icon: fullTrashIcon,
          variant: DropDownItemVariant.DESTRUCTIVE,
        },
      ],
    ],
  },
}

export const WithoutIcons: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    items: [
      [
        { text: 'Ajouter' },
        { text: 'Modifier' },
        { text: 'Supprimer', variant: DropDownItemVariant.DESTRUCTIVE },
      ],
    ],
  },
}

export const WithSeparators: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    items: [
      [{ text: 'Ajouter', icon: fullPlusIcon }],
      [{ text: 'Modifier', icon: fullEditIcon }],
      [
        {
          text: 'Supprimer',
          icon: fullTrashIcon,
          variant: DropDownItemVariant.DESTRUCTIVE,
        },
      ],
    ],
  },
}

export const ForcedSideRight: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    side: 'right',
  },
}

export const ForcedSideRightAndAlignedEnd: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    side: 'right',
    align: 'end',
  },
}

export const WidthTrigger: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    width: 'trigger',
    label: "Trigger d'une certaine longueur",
  },
}

export const WidthNumber: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    width: 650,
    label: 'Dropdown largeur fixe (650px)',
  },
}

export const WithTags: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    items: [
      [
        {
          text: 'Pré-réserver',
          tag: { label: 'Nouveau', variant: TagVariant.NEW },
        },
        {
          text: 'Partager',
          tag: { label: 'J’aime', variant: TagVariant.LIKE },
        },
        {
          text: 'Transcription',
          tag: { label: 'Pour les livres', variant: TagVariant.CINECLUB },
        },
      ],
    ],
  },
}

export const NavigationLinks: StoryObj<typeof Dropdown> = {
  args: {
    ...DEFAULT_ARGS,
    items: [
      [
        {
          text: 'Accueil Storybook',
          link: {
            to: 'https://pass-culture.github.io/pass-culture-main/',
            target: '_blank',
          },
          icon: fullLogoutIcon,
        },
        {
          text: 'Google',
          link: { to: 'https://google.fr', target: '_blank' },
          icon: fullLinkIcon,
        },
      ],
    ],
  },
}

export const OnOpenChangeExample: StoryObj<typeof Dropdown> = {
  render: () => {
    const [isOpen, setIsOpen] = useState(false)

    return (
      <>
        <pre style={{ marginBottom: '16px  ' }}>
          isOpen: {isOpen ? 'true' : 'false'}
        </pre>
        <Dropdown
          label="Dropdown"
          trigger={
            <Button
              label="Dropdown"
              variant={ButtonVariant.PRIMARY}
              icon={isOpen ? fullUpIcon : fullDownIcon}
              iconPosition={IconPositionEnum.RIGHT}
            />
          }
          open={isOpen}
          onOpenChange={setIsOpen}
          items={[
            [
              { text: 'Ajouter', icon: fullPlusIcon },
              { text: 'Modifier', icon: fullEditIcon },
              {
                text: 'Supprimer',
                icon: fullTrashIcon,
                variant: DropDownItemVariant.DESTRUCTIVE,
              },
            ],
          ]}
        />
      </>
    )
  },
}

export const onSelectActions: StoryObj<typeof Dropdown> = {
  render: () => {
    const [isDownloading, setIsDownloading] = useState(false)
    const [downloadProgress, setDownloadProgress] = useState(0)

    const interval = useRef<NodeJS.Timeout | null>(null)

    const startDownload = () => {
      setIsDownloading(true)
      interval.current = setInterval(() => {
        setDownloadProgress((prev) => prev + 0.01)

        if (downloadProgress >= 1) {
          stopDownload()
        }
      }, 100)
    }

    const pauseDownload = () => {
      setIsDownloading(false)
      if (interval.current) {
        clearInterval(interval.current)
        interval.current = null
      }
    }

    const stopDownload = () => {
      pauseDownload()
      setDownloadProgress(0)
    }

    const shouldSeeProgressBar = isDownloading || downloadProgress > 0

    const itemsDefault = [
      [
        {
          text: downloadProgress > 0 ? 'Reprendre' : 'Télécharger',
          onSelect: startDownload,
          icon: fullDownloadIcon,
        },
      ],
    ]

    const itemsWhenDownloading = [
      [
        {
          text: 'Annuler',
          onSelect: stopDownload,
          icon: fullClearIcon,
          variant: DropDownItemVariant.DESTRUCTIVE,
        },
      ],
      [{ text: 'Pause', onSelect: pauseDownload, icon: fullPauseIcon }],
    ]

    return (
      <>
        <Dropdown
          label="Choose an action"
          side="top"
          align="start"
          items={isDownloading ? itemsWhenDownloading : itemsDefault}
        />
        <br />
        <br />
        {shouldSeeProgressBar ? (
          <>
            <p>Téléchargement en cours…</p>
            <progress value={downloadProgress} max={1} />
          </>
        ) : (
          <p>—</p>
        )}
      </>
    )
  },
}

export const WithCustomTriggerAndAriaLabel: StoryObj<typeof Dropdown> = {
  render: () => {
    const [color, setColor] = useState('red')
    return (
      <div
        style={{
          display: 'inline-flex',
          gap: '10px',
          alignItems: 'center',
          justifyContent: 'space-around',
        }}
      >
        <Dropdown
          items={[
            [
              { text: 'Rouge', onSelect: () => setColor('red') },
              { text: 'Vert', onSelect: () => setColor('green') },
              { text: 'Bleu', onSelect: () => setColor('blue') },
            ],
          ]}
          side="left"
          align="start"
          trigger={
            <div
              tabIndex={1}
              style={{
                backgroundColor: color,
                borderRadius: '25px',
                width: '50px',
                height: '50px',
                cursor: 'pointer',
              }}
            />
          }
          label="Custom trigger label"
        />
        <Dropdown
          items={[
            [
              { text: 'Ajouter' },
              { text: 'Modifier' },
              { text: 'Supprimer', variant: DropDownItemVariant.DESTRUCTIVE },
            ],
          ]}
          side="right"
          align="start"
          trigger={
            <Button
              tabIndex={2}
              variant={ButtonVariant.SECONDARY}
              icon={fullThreeDotsIcon}
            />
          }
          label="Open options"
        />
      </div>
    )
  },
}
