import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import styles from '@/pages/WelcomeCarousel/WelcomeCarousel.module.scss'

import commonStyles from '../CommonWelcomeCarousel.module.scss'

const WelcomeStepAdvantages = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>
        Pourquoi rejoindre le pass Culture ?
      </h1>
      <h2 className={commonStyles.subtitle}>
        Découvrez les avantages pour votre structure
      </h2>
      <div className={commonStyles[`container`]}>
        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusamus, at
        beatae commodi delectus dicta dolorem error laboriosam laudantium odit
        quasi. Distinctio dolores in inventore maxime nemo porro repudiandae
        saepe velit!
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
          className={styles['actionbar-container-stepper']}
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
