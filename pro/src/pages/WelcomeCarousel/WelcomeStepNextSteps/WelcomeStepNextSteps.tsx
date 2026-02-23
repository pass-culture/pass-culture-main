import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import commonStyles from '../CommonWelcomeCarousel.module.scss'

const WelcomeStepNextSteps = (): JSX.Element => {
  return (
    <>
      <h1 className={commonStyles.title}>Comment fonctionne l’inscription ?</h1>
      <h2 className={commonStyles.subtitle}>
        3 étapes simples avant d’être visible sur le pass Culture
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
