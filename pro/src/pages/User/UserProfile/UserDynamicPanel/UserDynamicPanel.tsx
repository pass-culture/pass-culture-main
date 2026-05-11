import type { ReactNode } from 'react'

import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'

import type { Forms } from '../constants'

interface UserDynamicPanelProps {
  title: string
  form: Forms
  currentForm: Forms | null
  setCurrentForm: (form: Forms | null) => void
  children: (closeForm: () => void) => ReactNode
  displayContent: ReactNode
}

export const UserDynamicPanel = ({
  title,
  form,
  currentForm,
  setCurrentForm,
  children,
  displayContent,
}: UserDynamicPanelProps): JSX.Element => {
  const isOpen = currentForm === form

  const open = () => setCurrentForm(form)
  const close = () => setCurrentForm(null)

  return (
    <SummarySection
      title={title}
      editLink={
        <Button
          label={isOpen ? 'Fermer' : 'Modifier'}
          onClick={isOpen ? close : open}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
        />
      }
      shouldShowDivider
    >
      {isOpen ? children(close) : displayContent}
    </SummarySection>
  )
}
