import React, { ReactNode } from 'react'
import { unstable_useBlocker } from 'react-router-dom'
import type { Location } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'

export type BlockerFunction = (args: {
  currentLocation: Location
  nextLocation: Location
}) => boolean

export interface RouteLeavingGuardProps {
  children?: ReactNode | ReactNode[]
  extraClassNames?: string
  shouldBlockNavigation: BlockerFunction
  dialogTitle: string
  tracking?: (p: string) => void
  rightButton?: string
  leftButton?: string
  // This is a weird behavior that should be unified at a UX level
  // the modal should follow the same behavior
  closeModalOnRightButton?: boolean
}

const RouteLeavingGuard = ({
  children,
  extraClassNames = '',
  shouldBlockNavigation,
  dialogTitle,
  tracking,
  rightButton = 'Quitter',
  leftButton = 'Annuler',
  closeModalOnRightButton = false,
}: RouteLeavingGuardProps) => {
  const blocker = unstable_useBlocker(shouldBlockNavigation)

  const closeModal = () => {
    if (blocker.state !== 'blocked') {
      return
    }
    blocker.reset()
  }

  const confirmNavigation = () => {
    if (blocker.state !== 'blocked') {
      return
    }

    if (tracking) {
      tracking(blocker.location.pathname)
    }
    blocker.proceed()
  }

  return blocker.state === 'blocked' ? (
    <ConfirmDialog
      extraClassNames={extraClassNames}
      onCancel={closeModal}
      leftButtonAction={
        closeModalOnRightButton ? confirmNavigation : closeModal
      }
      onConfirm={closeModalOnRightButton ? closeModal : confirmNavigation}
      title={dialogTitle}
      confirmText={rightButton}
      cancelText={leftButton}
    >
      {children}
    </ConfirmDialog>
  ) : null
}

export default RouteLeavingGuard
