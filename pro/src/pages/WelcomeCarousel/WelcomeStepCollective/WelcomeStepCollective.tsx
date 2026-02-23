import cn from 'classnames'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeEventIcon from '@/icons/stroke-events.svg'
import strokeHourglassIcon from '@/icons/stroke-hourglass.svg'
import { CardInfo } from '@/pages/WelcomeCarousel/components/CardInfo'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepCollective.module.scss'

const WelcomeStepCollective = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>Offres pour les groupes scolaires</h1>
      <h2 className={commonStyles.subtitle}>Intervenez auprès des classes</h2>
      <div className={cn(commonStyles[`container`], styles['container'])}>
        <CardInfo icon={strokeEventIcon} title="Qui réserve ?">
          Le corps enseignant réserve pour les classes (de la 6e à la Terminale)
          via la plateforme ADAGE.
        </CardInfo>
        <CardInfo icon={strokeEuroIcon} title="Comment ça fonctionne ?">
          Déposez votre dossier ADAGE pour obtenir un référencement. Les
          établissements paient avec leur budget pass Culture. Vous recevez le
          paiement sous 2 à 3 semaines.
        </CardInfo>
        <CardInfo
          icon={strokeHourglassIcon}
          title="Combien de temps ça prend ?"
        >
          pass Culture Pro : quelques jours. Référencement ADAGE : 2 à 9 mois
          (selon commissions régionales). Vous pouvez démarrer avec des offres
          via l’application destinée aux jeunes en attendant.
        </CardInfo>
        <div className={styles['footer']}>
          <Button
            as="a"
            label="Exemple d’offres pour les groupes scolaires"
            variant={ButtonVariant.TERTIARY}
            size={ButtonSize.SMALL}
            isExternal
            opensInNewTab
            to="https://aide.passculture.app/hc/fr/articles/21872145727388--Acteurs-culturels-Consulter-des-exemples-d-offres-r%C3%A9servables"
          />
        </div>
      </div>
      <div className={commonStyles[`actionbar-container`]}>
        <Button
          as="a"
          to="/bienvenue/offres-jeunes"
          variant={ButtonVariant.SECONDARY}
          label="Précédent"
        />
        <BubbleStepper
          page={3}
          total={4}
          className={commonStyles['actionbar-container-stepper']}
        />
        <Button
          as="a"
          to="/bienvenue/avantages"
          variant={ButtonVariant.PRIMARY}
          label="Suivant"
        />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepCollective
