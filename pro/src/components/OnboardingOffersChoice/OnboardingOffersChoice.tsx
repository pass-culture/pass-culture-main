import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { OnboardingDidacticEvents } from '@/commons/core/FirebaseEvents/constants'
import { Dialog } from '@/components/Dialog/Dialog'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Card } from '@/ui-kit/Card/Card'

import collective from './assets/collective.jpeg'
import individuelle from './assets/individuelle.jpeg'
import { OnboardingCollectiveModal } from './components/OnboardingCollectiveModal/OnboardingCollectiveModal'
import styles from './OnboardingOffersChoice.module.scss'

export const OnboardingOffersChoice = () => {
  const [showModal, setShowModal] = useState(false)
  const { logEvent } = useAnalytics()

  return (
    <div className={styles['card-container']}>
      <Card
        imageSrc={individuelle}
        title={
          <h3 className={styles['card-title']}>
            Sur l’application mobile à destination des jeunes
          </h3>
        }
        actions={
          <Button
            as="a"
            variant={ButtonVariant.PRIMARY}
            to="/onboarding/individuel"
            aria-label="Commencer la création d’offre sur l’application mobile"
            fullWidth
            label="Commencer"
          />
        }
      >
        Vos offres seront visibles par{' '}
        <strong className={styles['card-description-highlight']}>
          + de 4 millions de jeunes{' '}
        </strong>
        inscrits sur l’application mobile pass Culture.
      </Card>

      <Card
        imageSrc={collective}
        title={
          <h3 className={styles['card-title']}>
            Sur ADAGE à destination des enseignants
          </h3>
        }
        actions={
          <Dialog
            title=""
            onCancel={() => setShowModal(false)}
            hideIcon={true}
            trigger={
              <Button
                type="submit"
                aria-label="Commencer la création d’offre sur ADAGE"
                onClick={() => {
                  logEvent(
                    OnboardingDidacticEvents.HAS_CLICKED_START_COLLECTIVE_DIDACTIC_ONBOARDING
                  )
                  setShowModal(true)
                }}
                fullWidth
                label="Commencer"
              />
            }
            open={showModal}
          >
            <OnboardingCollectiveModal />
          </Dialog>
        }
      >
        Vos offres seront visibles{' '}
        <strong className={styles['card-description-highlight']}>
          par tous les enseignants
        </strong>{' '}
        des collèges et lycées publics et privés sous contrat.
      </Card>
    </div>
  )
}
