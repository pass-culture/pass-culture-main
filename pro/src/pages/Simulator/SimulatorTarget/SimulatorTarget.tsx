import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

export const SimulatorTarget = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Quels publics souhaitez-vous cibler ?
        </h1>
      </div>
      <div className={commonStyles['action-bar']}>
        <Button
          as="a"
          to="/inscription/preparation/activite"
          variant={ButtonVariant.SECONDARY}
          label="Retour"
        />
        <BubbleStepper
          page={3}
          total={3}
          className={commonStyles['action-bar-stepper']}
        />
        <Button
          as="a"
          to="/inscription/preparation/resultats"
          label="Continuer"
        />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorTarget
