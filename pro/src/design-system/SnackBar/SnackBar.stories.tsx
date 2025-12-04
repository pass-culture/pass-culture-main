import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { INITIAL_VIEWPORTS } from 'storybook/viewport'

import { SnackBar, SnackBarVariant } from './SnackBar'

const meta: Meta<typeof SnackBar> = {
  title: '@/design-system/SnackBar',
  component: SnackBar,
  parameters: {
    viewport: {
      options: INITIAL_VIEWPORTS,
    },
  },
}

export default meta
type Story = StoryObj<typeof SnackBar>

export const Default: Story = {
  parameters: {
    docs: {
      title: 'Notification de succès',
      description: {
        story: 'Démonstration d\'une notification de succès.',
      },
    },
  },
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'Snack Bar par défaut',
    autoClose: false, // Pas de fermeture auto dans Storybook
    testId: 'default-success-snack-bar',
  },
}

export const Error: Story = {
  args: {
    variant: SnackBarVariant.ERROR,
    text: 'Snack Bar avec une erreur',
    autoClose: false,
    testId: 'error-snack-bar',
  },
  parameters: {
    docs: {
      title: 'Notification d\'erreur',
      description: {
        story: 'Démonstration d\'une notification d\'erreur.',
      },
    },
  },
}

export const LongMessageSuccess: Story = {
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'Snack Bar avec un message très long qui dure 10 secondes au lieu de 5 secondes par défaut (car il contient plus de 120 caractères)',
    autoClose: false,
    testId: 'long-message-success-snack-bar',
  },
}

type Notification = {
  id: number
  variant: SnackBarVariant
  text: string
}

export const Playground: StoryObj<typeof SnackBar> = {
  parameters: {
    docs: {
      description: {
        story:
          'Démonstration du stacking de plusieurs notifications. Cliquez sur les boutons pour ajouter des notifications qui se stackent en bas à droite.',
      },
    },
  },
  render: (args) => {
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [counter, setCounter] = useState(0)
  
    const addNotification = (variant: SnackBarVariant, text: string) => {
      const id = counter
      setCounter((prev) => prev + 1)
      setNotifications((prev) => [...prev, { id, variant, text }])
    }
  
    const removeNotification = (id: number) => {
      setNotifications((prev) => prev.filter((n) => n.id !== id))
    }

    return (
      <div style={{ height: '500px' }}>
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', flexDirection: 'column', alignItems: 'flex-start' }}>
        <button
          onClick={() =>
            addNotification(
              SnackBarVariant.SUCCESS,
              'Notification de succès'
            )
          }
        >
          Ajouter une notification de succès
        </button>
        <button
          onClick={() =>
            addNotification(
              SnackBarVariant.ERROR,
              "Notification d'erreur"
            )
          }
        >
          Ajouter une notification d'erreur
        </button>
        <button
          onClick={() =>
            addNotification(
              SnackBarVariant.SUCCESS,
              'Ceci est un message très long pour démontrer que la durée est de 10 secondes au lieu de 5 secondes quand le texte dépasse 120 caractères.'
            )
          }
        >
          Ajouter une notification de succès avec un message long
        </button>
        <button onClick={() => setNotifications([])}>
          Effacer toutes les notifications
        </button>
      </div>
      <div
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: '8px',
          zIndex: 1000,
        }}
      >
        {notifications.map((notif) => (
          <SnackBar
            key={notif.id}
            variant={notif.variant}
            text={notif.text}
            onClose={() => removeNotification(notif.id)}
            autoClose={true}
            testId={`snack-bar-${notif.id}`}
          />
        ))}
      </div>
    </div>
    )
  }
}