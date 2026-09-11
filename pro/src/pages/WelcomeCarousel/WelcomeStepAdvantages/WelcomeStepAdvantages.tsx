import cn from 'classnames'

import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import strokeProfilIcon from '@/icons/stroke-profil.svg'
import strokeReleaseIcon from '@/icons/stroke-release.svg'
import { InfoPanelList } from '@/ui-kit/InfoPanelList/InfoPanelList'
import {
  InfoPanelSize,
  InfoPanelSurface,
  InfoPanelVariant,
} from '@/ui-kit/InfoPanelList/types'

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
        <InfoPanelList
          variant={InfoPanelVariant.UNORDERED}
          surface={InfoPanelSurface.FLAT}
          size={InfoPanelSize.LARGE}
          panels={[
            {
              title: '4 millions de jeunes',
              description:
                "Touchez une audience de 15-21 ans partout en France, activement à la recherche d'expériences culturelles",
              icon: strokeProfilIcon,
            },
            {
              title: 'Une inscription simple et rapide',
              description:
                "Contrairement aux appels à projet lourds et complexes, l'inscription à pass Culture Pro est simple et guidée",
              icon: strokeReleaseIcon,
            },
            {
              title: 'Publiez quand vous voulez',
              description:
                'Créez et modifiez vos offres, qu’elles soient gratuites ou payantes, à tout moment de l’année',
              icon: strokeOfferIcon,
            },
          ]}
        />
      </div>
      <div className={commonStyles['actionbar-container']}>
        <Button
          as="router-link"
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
          as="router-link"
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
