import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepIndividual.module.scss'

const WelcomeStepIndividual = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles['title']}>
        Deux manières de vous faire connaître
      </h1>

      <h2 className={commonStyles['subtitle']}>
        Les jeunes peuvent découvrir vos offres de deux façons différentes :
      </h2>

      <div className={commonStyles[`container`]}>
        <ol className={styles['ways-list']}>
          <li className={styles['way-item']}>
            1) Via{' '}
            <em className={styles['rotation-clockwise-inverted']}>
              l’application
            </em>{' '}
            pass Culture dédiée aux{' '}
            <em className={styles['rotation-clockwise']}>jeunes</em>
          </li>
          <li className={styles['way-item']}>
            2) Via ADAGE pour les{' '}
            <em className={styles['rotation-clockwise']}>groupes scolaires</em>
          </li>
        </ol>

        <Banner
          title="Vous pourrez cumuler les deux types d’offres avec un seul compte pass
          Culture Pro."
        />

        <div className={commonStyles[`actionbar-container`]}>
          <Button
            as="a"
            to="/bienvenue"
            variant={ButtonVariant.SECONDARY}
            label="Précédent"
          />
          <BubbleStepper
            page={1}
            total={4}
            className={styles['actionbar-container-stepper']}
          />
          <Button
            as="a"
            to="/bienvenue/offres-jeunes"
            variant={ButtonVariant.PRIMARY}
            label="Suivant"
          />
        </div>
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepIndividual
