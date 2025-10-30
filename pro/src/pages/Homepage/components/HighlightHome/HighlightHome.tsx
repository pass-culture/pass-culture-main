import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
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
              >
                Parcourir les temps forts
              </Button>
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
