import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import highlightImg from './assets/highlight.png'
import styles from './HighlightHome.module.scss'
import { ModalHighlight } from './ModalHighlight/ModalHighlight'

export const HighlightHome = () => {
  const [isOpen, setIsOpen] = useState(false)
  const { logEvent } = useAnalytics()

  return (
    <div className={styles['highlight-home']}>
      <Card
        imageSrc={highlightImg}
        title={
          <h3 className={styles['highlight-title']}>
            Valorisez vos évènements en les associant à un temps fort du pass
            Culture !
          </h3>
        }
        actions={
          <ModalHighlight
            onOpenChange={setIsOpen}
            open={isOpen}
            trigger={
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={() =>
                  logEvent(HighlightEvents.HAS_CLICKED_DISCOVER_HIGHLIGHT)
                }
                label="Parcourir les temps forts"
              />
            }
          />
        }
      >
        Un temps fort permet de valoriser vos offres évènements autour d’une
        thématique.
      </Card>
    </div>
  )
}
