import { ReactNode, useState } from 'react'

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

  return (
    <div className={styles['card-container']}>
      <Card
        imageSrc={individuelle}
        title="Aux jeunes sur l’application mobile pass Culture"
        actions={
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to="/onboarding/individuel"
            title="Commencer la création d’offre sur l’application mobile"
          >
            Commencer
          </ButtonLink>
        }
      >
        Vos offres seront visibles par{' '}
        <strong className={styles['card-description-highlight']}>
          + de 4 millions de jeunes
        </strong>
        .
      </Card>

      <Card
        imageSrc={collective}
        title="Aux enseignants sur la plateforme ADAGE"
        actions={
          <Dialog
            title=""
            onCancel={() => setShowModal(false)}
            hideIcon={true}
            trigger={
              <Button
                type="submit"
                title="Commencer la création d’offre sur ADAGE"
                onClick={() => setShowModal(true)}
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
        Vos offres seront visibles par{' '}
        <strong className={styles['card-description-highlight']}>
          tous les enseignants
        </strong>{' '}
        des collèges et lycées publics et privés sous contrat.
      </Card>
    </div>
  )
}
