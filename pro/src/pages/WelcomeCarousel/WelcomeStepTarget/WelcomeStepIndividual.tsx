import commonStyles from '@/pages/WelcomeCarousel/WelcomeCarousel.module.scss'

const WelcomeStepIndividual = (): JSX.Element => {
  return (
    <div className={commonStyles[`container`]}>
      Lorem ipsum dolor sit amet, consectetur adipisicing elit. Accusamus, at
      beatae commodi delectus dicta dolorem error laboriosam laudantium odit
      quasi. Distinctio dolores in inventore maxime nemo porro repudiandae saepe
      velit!
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeStepIndividual
