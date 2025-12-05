import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { INITIAL_VIEWPORTS } from 'storybook/viewport'

import { SnackBar, SnackBarProps, SnackBarVariant } from './SnackBar'

/**
 * Meta object for the SnackBar component.
 */
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

/**
 * Story type for the SnackBar component.
 */
type Story = StoryObj<typeof SnackBar>

/**
 * Wrapper interactif with a reopen button.
 * @param args - The props for the SnackBar component.
 * @returns The SnackBar component with a reopen button.
 */
const SnackBarWithReopenButton = (args: SnackBarProps) => {
  const [isVisible, setIsVisible] = useState(true)

  return (
    <div>
      {!isVisible && (
        <button onClick={() => setIsVisible(true)}>Afficher la notification</button>
      )}
      <SnackBar {...args} isVisible={isVisible} onClose={() => setIsVisible(false)}/>
    </div>
  )
}

/**
 * Story for the default SnackBar component.
 */
export const Default: Story = {
  parameters: {
    docs: {
      title: 'Notification de succès',
      description: {
        story: 'Démonstration d\'une notification de succès.',
      },
    },
  },
  render: (args) => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'Snack Bar par défaut',
    autoClose: false,
    testId: 'default-success-snack-bar',
  },
}

/**
 * Story for the error SnackBar component.
 */
export const Error: Story = {
  render: (args) => <SnackBarWithReopenButton {...args} />,
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

/**
 * Story for the long message success SnackBar component.
 */
export const LongMessageSuccess: Story = {
  render: (args) => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'Snack Bar avec un message très long qui dure 10 secondes au lieu de 5 secondes par défaut (car il contient plus de 120 caractères)',
    autoClose: false,
    testId: 'long-message-success-snack-bar',
  },
}

/**
 * Notification type.
 */
type Notification = {
  id: number
  variant: SnackBarVariant
  text: string
}

/**
 * Playground for the SnackBar component.
 */
export const Playground: Story = {
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
        <button onClick={() => addNotification(SnackBarVariant.SUCCESS, 'Notification de succès')}>Ajouter une notification de succès</button>
        <button onClick={() => addNotification(SnackBarVariant.ERROR, 'Notification d\'erreur')}>Ajouter une notification d'erreur</button>
        <button onClick={() => addNotification(SnackBarVariant.SUCCESS, 'Ceci est un message très long pour démontrer que la durée est de 10 secondes au lieu de 5 secondes quand le texte dépasse 120 caractères.')}>
          Ajouter une notification de succès avec un message long.
        </button>
        <button onClick={() => setNotifications([])}>Effacer toutes les notifications.</button>
      </div>
      <div style={{alignItems: 'flex-end', bottom: '24px', display: 'flex', flexDirection: 'column', gap: '8px', position: 'fixed', right: '24px', zIndex: 1000,}}>
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