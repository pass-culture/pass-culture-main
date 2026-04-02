import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import styles from './ActionBar.module.scss'

interface ActionBarProps {
  nextTo?: string
  onClickNext?: () => void
  previousTo?: string
  onClickPrevious?: () => void
  nextTitle?: string
  previousTitle?: string
  showBackButton?: boolean
}

export const ActionBar = ({
  nextTo,
  onClickNext,
  previousTo,
  onClickPrevious,
  nextTitle = 'Continuer',
  previousTitle = 'Retour',
  showBackButton = true,
}: ActionBarProps) => {
  return (
    <div className={styles['action-bar']}>
      {showBackButton && previousTo && (
        <Button
          as="a"
          to={previousTo}
          onClick={() => {
            onClickPrevious?.()
          }}
          variant={ButtonVariant.SECONDARY}
          label={previousTitle}
        />
      )}

      {nextTo && (
        <Button
          as="a"
          to={nextTo}
          onClick={() => {
            onClickNext?.()
          }}
          label={nextTitle}
        />
      )}
      {!nextTo && (
        <Button
          onClick={() => {
            onClickNext?.()
          }}
          label={nextTitle}
        />
      )}
    </div>
  )
}
