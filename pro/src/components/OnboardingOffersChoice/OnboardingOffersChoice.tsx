import { ReactNode } from 'react'

import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import collective from './assets/collective.jpeg'
import individuelle from './assets/individuelle.jpeg'
import styles from './OnboardingOffersChoicem.module.scss'

interface CardProps {
  imageSrc: string
  title: string
  children: ReactNode
  to?: string
}

const Card = ({ imageSrc, title, children, to }: CardProps) => {
  return (
    <div className={styles['card']}>
      <div className={styles['card-content']}>
        <div>
          <img src={imageSrc} alt="" className={styles['card-image']} />
          <h3 className={styles['card-title']}>{title}</h3>
          <p className={styles['card-description']}>{children}</p>
        </div>
        <div className={styles['card-button']}>
          {to ? (
            <ButtonLink variant={ButtonVariant.PRIMARY} to={to}>
              Commencer
            </ButtonLink>
          ) : (
            <Button type="submit">Commencer</Button>
          )}
        </div>
      </div>
    </div>
  )
}

export const OnboardingOffersChoice = () => {
  return (
    <div className={styles['card-container']}>
      <Card
        imageSrc={individuelle}
        title="Aux jeunes sur l’application mobile pass Culture"
        to={'/inscription-offre-individuelle'}
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
