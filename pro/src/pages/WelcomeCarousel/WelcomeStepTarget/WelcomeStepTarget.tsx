import cn from 'classnames'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Title } from '@/ui-kit/Title/Title'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepTarget.module.scss'

const WelcomeStepTarget = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['title-wrapper']}>
        <Title
          level="1"
          title="Deux manières de vous faire connaître"
          marginBottom="s"
        />
      </div>

      <p className={commonStyles['subtitle']}>
        Les jeunes peuvent découvrir vos offres de deux façons différentes :
      </p>

      <div className={commonStyles[`container`]}>
        <ol className={styles['ways-list']}>
          <li className={styles['way-item']}>
            1) Via{' '}
            <em
              className={cn(
                styles['emphasis'],
                styles['rotation-clockwise-inverted']
              )}
            >
              l’application
            </em>{' '}
            pass Culture dédiée aux{' '}
            <em
              className={cn(styles['emphasis'], styles['rotation-clockwise'])}
            >
              jeunes
            </em>
          </li>
          <li className={styles['way-item']}>
            2) Via ADAGE pour les{' '}
            <em
              className={cn(styles['emphasis'], styles['rotation-clockwise'])}
            >
              groupes scolaires
            </em>
          </li>
        </ol>

        <Banner
          title="Vous pourrez cumuler les deux types d’offres avec un seul compte pass
          Culture Pro."
        />

        <div className={commonStyles['actionbar-container']}>
          <Button
            as="router-link"
            to="/bienvenue"
            variant={ButtonVariant.SECONDARY}
            label="Précédent"
          />
          <BubbleStepper
            page={1}
            total={4}
            className={commonStyles['actionbar-container-stepper']}
          />
          <Button
            as="router-link"
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
export const Component = WelcomeStepTarget
