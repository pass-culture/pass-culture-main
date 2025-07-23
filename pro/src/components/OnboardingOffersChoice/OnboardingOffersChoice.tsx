import { ReactNode, useState } from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { OnboardingDidacticEvents } from 'commons/core/FirebaseEvents/constants'
import { Dialog } from 'components/Dialog/Dialog'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import collective from './assets/collective.jpeg'
import individuelle from './assets/individuelle.jpeg'
import { OnboardingCollectiveModal } from './components/OnboardingCollectiveModal/OnboardingCollectiveModal'
import styles from './OnboardingOffersChoice.module.scss'

interface CardProps {
  imageSrc: string
  title: string
  children: ReactNode
  actions: ReactNode
}

const Card = ({ imageSrc, title, children, actions }: CardProps) => {
  return (
    <div className={styles['card']}>
      <div className={styles['card-content']}>
        <div>
          <img src={imageSrc} alt="" className={styles['card-image']} />
          <h3 className={styles['card-title']}>{title}</h3>
          <p className={styles['card-description']}>{children}</p>
        </div>
        <div className={styles['card-button']}>{actions}</div>
      </div>
    </div>
  )
}

export const OnboardingOffersChoice = () => {
  const [showModal, setShowModal] = useState(false)
  const { logEvent } = useAnalytics()

  return (
    <div className={styles['card-container']}>
      <Card
        imageSrc={individuelle}
        title="Sur l’application mobile à destination des jeunes"
        actions={
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to="/onboarding/individuel"
            aria-label="Commencer la création d’offre sur l’application mobile"
            className={styles['button-getting-started']}
          >
            Commencer
          </ButtonLink>
        }
      >
        Vos offres seront visibles par{' '}
        <strong className={styles['card-description-highlight']}>
          + de 4 millions de jeunes
        </strong>
        inscrits sur l’application mobile pass Culture.
      </Card>

      <Card
        imageSrc={collective}
        title="Sur ADAGE à destination des enseignants"
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
                className={styles['button-getting-started']}
              >
                Commencer
              </Button>
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
