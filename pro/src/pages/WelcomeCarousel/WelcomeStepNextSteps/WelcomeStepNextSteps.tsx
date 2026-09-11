import cn from 'classnames'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { WEBINAR_INDIVIDUAL } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import { InfoPanelList } from '@/ui-kit/InfoPanelList/InfoPanelList'
import {
  InfoPanelSize,
  InfoPanelSurface,
  InfoPanelVariant,
} from '@/ui-kit/InfoPanelList/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepNextSteps.module.scss'

const WelcomeStepNextSteps = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  const isPreSignupSimulatorFeatureActive = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )
  return (
    <>
      <h1 className={commonStyles.title}>Comment fonctionne l’inscription ?</h1>
      <h2 className={commonStyles.subtitle}>
        3 étapes simples avant d’être visible sur le pass Culture
      </h2>
      <div className={commonStyles[`container`]}>
        <div className={styles['steps']}>
          <InfoPanelList
            variant={InfoPanelVariant.ORDERED}
            surface={InfoPanelSurface.ELEVATED}
            size={InfoPanelSize.SMALL}
            panels={[
              {
                title:
                  'Décrivez votre structure et votre activité culturelle - 5 minutes',
                description:
                  'Renseignez les informations administratives et les domaines dans lesquels vous intervenez',
              },
              {
                title: 'Nos équipes valident votre inscription - 48 heures',
                description:
                  'Elles peuvent demander des documents complémentaires. Les offres scolaires nécessitent aussi que votre dossier Adage soit validé par des équipes externes.',
              },
              {
                title: 'Créez vos premières offres - 3 minutes',
                description:
                  "Créez vos offres sur pass Culture Pro puis diffusez-les sur l'application pour les jeunes ou sur Adage.",
              },
            ]}
          />
        </div>
        <div className={styles['banner']}>
          <Banner
            title="Besoin de plus d'informations ?"
            actions={[
              {
                href: WEBINAR_INDIVIDUAL,
                icon: fullLinkIcon,
                iconAlt: 'Nouvelle fenêtre',
                isExternal: true,
                label: 'Participez à notre prochain webinaire',
                type: 'link',
                onClick() {
                  logEvent(WelcomeCarouselEvents.CLICKED_SEE_WEBINAR)
                },
              },
            ]}
          />
        </div>
      </div>
      <div
        className={cn(
          commonStyles['actionbar-container'],
          commonStyles['actionbar-container-single']
        )}
      >
        <Button
          as="router-link"
          to={
            isPreSignupSimulatorFeatureActive
              ? '/inscription/preparation/siret'
              : '/inscription/compte/creation'
          }
          variant={ButtonVariant.PRIMARY}
          label="Démarrer l’inscription"
        />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepNextSteps
