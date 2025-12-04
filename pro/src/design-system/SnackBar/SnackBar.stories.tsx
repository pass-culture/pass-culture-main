import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { INITIAL_VIEWPORTS } from 'storybook/viewport'

import { SnackBar, SnackBarProps, SnackBarVariant } from './SnackBar'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'

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
      {isVisible && <SnackBar {...args} onClose={() => setIsVisible(false)}/>}
    </div>
  )
}

/**
 * Story for the default SnackBar component.
 */
export const Default: Story = {
  parameters: {
    docs: {
      title: 'Notification success',
      description: {
        story: 'Demonstration of a success notification.',
      },
    },
  },
  render: (args) => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.SUCCESS,
    text: 'Default Snack Bar',
    autoClose: false,
    testId: 'default-success-snack-bar',
  },
}

/**
 * Story for the error SnackBar component.
 */
export const ErrorVariant: Story = {
  render: (args) => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    text: 'Snack Bar with an error',
    autoClose: false,
    testId: 'error-snack-bar',
  },
  parameters: {
    docs: {
      title: 'Error notification',
      description: {
        story: 'Demonstration of an error notification.',
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
    text: 'Snack Bar with a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-success-snack-bar',
  },
}

/**
 * Story for the long message success SnackBar component.
 */
export const LongMessageError: Story = {
  render: (args) => <SnackBarWithReopenButton {...args} />,
  args: {
    variant: SnackBarVariant.ERROR,
    text: 'Snack Bar with an error and a very long message that lasts 10 seconds instead of 5 seconds by default (because it contains more than 120 characters)',
    autoClose: false,
    testId: 'long-message-error-snack-bar',
  },
}

/**
 * Notification type.
 */
type Notification = {
  id: number
  variant: SnackBarVariant
  text: string
  date: Date
}

/**
 * Playground component for demonstrating multiple stacked notifications.
 */
const PlaygroundComponent = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [counter, setCounter] = useState(0)
  const isMobileScreen = useMediaQuery('(max-width: 600px)')

  const addNotification = (variant: SnackBarVariant, text: string) => {
    const id = counter
    setCounter((prev) => prev + 1)
    setNotifications((prev) => [...prev, { id, variant, text, date: new Date() }])
  }

  const removeNotification = (id: number) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  // Small (mobile/app): the last snackbar appears below the first one (ascending order)
  // Large (desktop/tablet): the last snackbar appears above the first one (descending order)
  const notificationsToDisplay = notifications.toSorted((a, b) => 
    (isMobileScreen ? 1 : -1) * (a.date.getTime() - b.date.getTime())
  );

  return (
    <div style={{ height: '500px' }}>
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', flexDirection: 'column', alignItems: 'flex-start' }}>
        <button onClick={() => addNotification(SnackBarVariant.SUCCESS, 'Success notification')}>Add a success notification</button>
        <button onClick={() => addNotification(SnackBarVariant.ERROR, 'Error notification')}>Add an error notification</button>
        <button onClick={() => addNotification(SnackBarVariant.SUCCESS, 'Ceci est un message très long pour démontrer que la durée est de 10 secondes au lieu de 5 secondes quand le texte dépasse 120 caractères.')}>
          Add a success notification with a long message.
        </button>
        <button onClick={() => setNotifications([])}>Clear all notifications.</button>
      </div>
      <div style={{alignItems: 'flex-end', bottom: '24px', display: 'flex', flexDirection: 'column', gap: '8px', position: 'fixed', right: '24px', zIndex: 1000,}}>
        {notificationsToDisplay.map((notif) => (
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

/**
 * Playground for the SnackBar component.
 */
export const Playground: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Demonstration of stacking multiple notifications. Click on the buttons to add notifications that stack on the bottom right.',
      },
    },
  },
  render: () => <PlaygroundComponent />,
}