import cn from 'classnames'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import strokeProfilIcon from '@/icons/stroke-profil.svg'
import strokeReleaseIcon from '@/icons/stroke-release.svg'
import { InfoPanel } from '@/ui-kit/InfoPanel/InfoPanel'
import { InfoPanelSize, InfoPanelSurface } from '@/ui-kit/InfoPanel/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'
import styles from './WelcomeStepAdvantages.module.scss'

export const WelcomeStepAdvantages = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>
        Pourquoi rejoindre le pass Culture ?
      </h1>
      <h2 className={commonStyles.subtitle}>
        Découvrez les avantages pour votre structure
      </h2>
      <div className={cn(commonStyles[`container`], styles['container'])}>
        <InfoPanel
          title="4 millions de jeunes"
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.LARGE}
          icon={strokeProfilIcon}
        >
          Touchez une audience de 15-21 ans partout en France, activement à la
          recherche d'expériences culturelles
        </InfoPanel>
        <InfoPanel
          title="Une inscription simple et rapide"
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.LARGE}
          icon={strokeReleaseIcon}
        >
          Contrairement aux appels à projet lourds et complexes, l'inscription à
          pass Culture Pro est simple et guidée
        </InfoPanel>
        <InfoPanel
          title="Publiez quand vous voulez"
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.LARGE}
          icon={strokeOfferIcon}
        >
          Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à
          tout moment de l’année
        </InfoPanel>
      </div>
      <div className={commonStyles[`actionbar-container`]}>
        <Button
          as="a"
          to="/bienvenue/offres-scolaires"
          variant={ButtonVariant.SECONDARY}
          label="Précédent"
        />
        <BubbleStepper
          page={4}
          total={4}
          className={commonStyles['actionbar-container-stepper']}
        />
        <Button
          as="a"
          to="/bienvenue/prochaines-etapes"
          variant={ButtonVariant.PRIMARY}
          label="Suivant"
        />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepAdvantages
