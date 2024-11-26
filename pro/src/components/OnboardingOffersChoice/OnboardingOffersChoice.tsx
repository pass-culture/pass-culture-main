import { Button } from 'ui-kit/Button/Button'

import collective from './collective.jpeg'
import individuelle from './individuelle.jpeg'
import styles from './OnboardingOffersChoicem.module.scss'

interface CardProps {
  imageSrc: string
  altText: string
  title: string
  description: string
  highlightText: string
}

const Card = ({
  imageSrc,
  altText,
  title,
  description,
  highlightText,
}: CardProps) => {
  return (
    <div className={styles['card']}>
      <img src={imageSrc} alt={altText} className={styles['card-image']} />
      <div className={styles['card-content']}>
        <h3 className={styles['card-title']}>{title}</h3>
        <p className={styles['card-description']}>
          {description}{' '}
          <strong className={styles['card-description-highlight']}>
            {highlightText}
          </strong>
        </p>
        <div className={styles['card-button']}>
          <Button type="submit">Commencer</Button>
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
        altText="Aux jeunes sur l’application mobile pass Culture"
        title="Aux jeunes sur l’application mobile pass Culture"
        description="Vos offres seront visibles par"
        highlightText="+ de 4 millions de jeunes"
      />
      <Card
        imageSrc={collective}
        altText="Aux enseignants sur la plateforme ADAGE"
        title="Aux enseignants sur la plateforme ADAGE"
        description="Vos offres seront visibles"
        highlightText="par tous les enseignants des collèges et lycées publics et privés sous contrat"
      />
    </div>
  )
}
