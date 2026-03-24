import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import highlightImg from './assets/highlight.png'
import styles from './HighlightHome.module.scss'
import { ModalHighlight } from './ModalHighlight/ModalHighlight'

export const HighlightHome = () => {
  const [isOpen, setIsOpen] = useState(false)
  const { logEvent } = useAnalytics()
  const selectedVenue = useAppSelector(ensureSelectedVenue)

  return (
    <div className={styles['highlight-home']}>
      <Card>
        <Card.Image src={highlightImg} alt="" />
        <Card.Header
          title="Valorisez vos évènements en les associant à un temps fort du pass Culture !"
          subtitle="Un temps fort permet de valoriser vos offres évènements autour d'une thématique."
        />
        <Card.Footer>
          <ModalHighlight
            onOpenChange={setIsOpen}
            open={isOpen}
            trigger={
              <Button
                variant={ButtonVariant.SECONDARY}
                onClick={() =>
                  logEvent(EngagementEvents.HAS_REQUESTED_HIGHLIGHTS, {
                    venueId: selectedVenue.id,
                    action: 'discover',
                  })
                }
                label="Parcourir les temps forts"
              />
            }
          />
        </Card.Footer>
      </Card>
    </div>
  )
}
