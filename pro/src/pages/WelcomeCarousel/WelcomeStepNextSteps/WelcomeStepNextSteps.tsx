import cn from 'classnames'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import { InfoPanel } from '@/ui-kit/InfoPanel/InfoPanel'
import { InfoPanelSize, InfoPanelSurface } from '@/ui-kit/InfoPanel/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepNextSteps.module.scss'

const WelcomeStepNextSteps = (): JSX.Element => {
  const { logEvent } = useAnalytics()
  return (
    <>
      <h1 className={commonStyles.title}>Comment fonctionne l’inscription ?</h1>
      <h2 className={commonStyles.subtitle}>
        3 étapes simples avant d’être visible sur le pass Culture
      </h2>
      <div className={commonStyles[`container`]}>
        <div className={styles['steps']}>
          <InfoPanel
            surface={InfoPanelSurface.ELEVATED}
            size={InfoPanelSize.SMALL}
            title="Décrivez votre structure et votre activité culturelle - 5 minutes"
            stepNumber={1}
          >
            Renseignez les informations administratives et les domaines dans
            lesquels vous intervenez
          </InfoPanel>
          <InfoPanel
            surface={InfoPanelSurface.ELEVATED}
            size={InfoPanelSize.SMALL}
            title="Nos équipes valident votre dossier - 48 heures"
            stepNumber={2}
          >
            Elles peuvent demander des documents complémentaires. Les offres
            scolaires nécessitent aussi une validation des équipes externes
            rattachées à Adage.
          </InfoPanel>
          <InfoPanel
            surface={InfoPanelSurface.ELEVATED}
            size={InfoPanelSize.SMALL}
            title="Créez vos premières offres - 3 minutes"
            stepNumber={3}
          >
            Créez vos offres sur pass Culture Pro puis diffusez-les sur
            l'application pour les jeunes ou sur Adage.
          </InfoPanel>
        </div>
        <div className={styles['banner']}>
          <Banner
            title="Besoin de plus d'informations ?"
            actions={[
              {
                href: '#', // TODO: jclery-pass (24/02/2026): Wait for target page to be ready
                icon: fullLinkIcon,
                iconAlt: 'Nouvelle fenêtre',
                label: 'Participez à notre prochain webinaire',
                type: 'link',
                onClick() {
                  logEvent(WelcomeCarouselEvents.CLICKED_SEE_WEBINAR, {
                    from: location.pathname,
                  })
                },
              },
            ]}
          />
        </div>
      </div>
      <div
        className={cn(
          commonStyles[`actionbar-container`],
          commonStyles[`actionbar-container-single`]
        )}
      >
        <Button
          as="a"
          to="/inscription/compte/creation"
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
