import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

export const SimulatorActivity = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Quelle est votre activité principale ?
        </h1>
      </div>
      <div className={commonStyles['action-bar']}>
        <Button
          as="a"
          to="/inscription/preparation/siret"
          variant={ButtonVariant.SECONDARY}
          label="Retour"
        />
        <BubbleStepper
          page={2}
          total={3}
          className={commonStyles['action-bar-stepper']}
        />
        <Button
          as="a"
          to="/inscription/preparation/publics"
          label="Continuer"
        />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorActivity
