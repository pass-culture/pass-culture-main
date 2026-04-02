import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'
import { ActionBar } from '@/pages/Simulator/components/ActionBar/ActionBar'

export const SimulatorTarget = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Quels publics souhaitez-vous cibler ?
        </h1>
      </div>
      <ActionBar
        previousTo="/inscription/preparation/activite"
        nextTo="/inscription/preparation/resultats"
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorTarget
