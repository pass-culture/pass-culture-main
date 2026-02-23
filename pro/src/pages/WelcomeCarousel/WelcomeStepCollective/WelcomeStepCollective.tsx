import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'

const WelcomeStepCollective = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>Offres pour les groupes scolaires</h1>
      <h2 className={commonStyles.subtitle}>Intervenez auprès des classes</h2>
      <div className={commonStyles[`container`]}>
        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusamus, at
        beatae commodi delectus dicta dolorem error laboriosam laudantium odit
        quasi. Distinctio dolores in inventore maxime nemo porro repudiandae
        saepe velit!
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
