import cn from 'classnames'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonSize, ButtonVariant } from '@/design-system/Button/types'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeEventIcon from '@/icons/stroke-events.svg'
import strokeHourglassIcon from '@/icons/stroke-hourglass.svg'
import { CardInfo } from '@/pages/WelcomeCarousel/components/CardInfo'
import { Title } from '@/ui-kit/Title/Title'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepCollective.module.scss'

const WelcomeStepCollective = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  return (
    <>
      <div className={commonStyles['title-wrapper']}>
        <Title
          level="1"
          title="Offres pour les groupes scolaires"
          marginBottom="s"
        />
      </div>
      <p className={commonStyles.subtitle}>Intervenez auprès des classes</p>
      <div className={cn(commonStyles[`container`], styles['container'])}>
        <CardInfo
          icon={strokeEventIcon}
          title="Qui réserve ?"
          titleLevel="2"
          description="Le corps enseignant réserve pour les classes (de la 6e à la Terminale)
          via la plateforme ADAGE."
        ></CardInfo>
        <CardInfo
          icon={strokeEuroIcon}
          title="Comment ça fonctionne ?"
          titleLevel="2"
          description="Déposez votre dossier ADAGE pour obtenir un référencement. Les
          établissements paient avec leur budget pass Culture. Vous recevez le
          paiement sous 2 à 3 semaines."
        ></CardInfo>
        <CardInfo
          icon={strokeHourglassIcon}
          title="Combien de temps ça prend ?"
          titleLevel="2"
          description="pass Culture Pro : quelques jours. Référencement ADAGE : 2 à 9 mois
          (selon commissions régionales). Vous pouvez démarrer avec des offres
          via l’application destinée aux jeunes en attendant."
        ></CardInfo>
        <div className={styles['footer']}>
          <Button
            as="a"
            label="Exemple d’offres pour les groupes scolaires"
            variant={ButtonVariant.TERTIARY}
            size={ButtonSize.SMALL}
            onClick={() => {
              logEvent(WelcomeCarouselEvents.CLICKED_SEE_COLLECTIVE_OFFERS)
            }}
            opensInNewTab
            to="https://aide.passculture.app/hc/fr/articles/21872145727388--Acteurs-culturels-Consulter-des-exemples-d-offres-r%C3%A9servables"
          />
        </div>
      </div>
      <div className={commonStyles['actionbar-container']}>
        <Button
          as="router-link"
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
          as="router-link"
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
