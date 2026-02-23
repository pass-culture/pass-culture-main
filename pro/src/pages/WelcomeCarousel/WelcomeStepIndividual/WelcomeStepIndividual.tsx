import fullLinkIcon from 'icons/full-link.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeEventsIcon from 'icons/stroke-events.svg'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import { CardInfo } from '../components/CardInfo'
import styles from './WelcomeStepIndividual.module.scss'

const WelcomeStepIndividual = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>
        Offres pour les jeunes via l’application
      </h1>

      <h2 className={commonStyles.subtitle}>
        Diffusez vos offres gratuites ou payantes auprès des 15-21 ans
      </h2>

      <div className={commonStyles['container']}>
        <div className={styles['cards']}>
          <CardInfo icon={strokeEventsIcon} title="Qui réserve ?">
            Les jeunes de 15 à 21 ans réservent directement via l'application
            pass Culture.
          </CardInfo>
          <CardInfo icon={strokeEuroIcon} title="Comment ça fonctionne ?">
            Les jeunes paient avec leur crédit personnel (50€ à 200€). Vous
            recevez le paiement sous 2 à 3 semaines.
          </CardInfo>
        </div>

        <div className={styles['helplink']}>
          <Button
            as="a"
            to="#" // TODO: jclery-pass (23/02/2026): Wait for help page to be created on https://aide.passculture.app
            label="Exemples d'offres pour les jeunes"
            icon={fullLinkIcon}
            variant={ButtonVariant.TERTIARY}
            size={ButtonSize.SMALL}
          />
        </div>
      </div>

      <div className={commonStyles['actionbar-container']}>
        <Button
          as="a"
          to="/bienvenue/publics"
          variant={ButtonVariant.SECONDARY}
          label="Précédent"
        />
        <BubbleStepper
          page={2}
          total={4}
          className={commonStyles['actionbar-container-stepper']}
        />
        <Button
          as="a"
          to="/bienvenue/offres-scolaires"
          variant={ButtonVariant.PRIMARY}
          label="Suivant"
        />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepIndividual
