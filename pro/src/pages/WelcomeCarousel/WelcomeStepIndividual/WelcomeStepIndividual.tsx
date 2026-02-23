import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/WelcomeCarousel/CommonWelcomeCarousel.module.scss'

const WelcomeStepIndividual = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>
        Offres pour les jeunes via l’application
      </h1>
      <h2 className={commonStyles.subtitle}>
        Diffusez vos offres gratuites ou payantes auprès des 15-21 ans
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
      </div>{' '}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepIndividual
