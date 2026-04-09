import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'
import { ActionBar } from '@/pages/Simulator/components/ActionBar/ActionBar'

export const SimulatorActivity = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Quelle est votre activité principale ?
        </h1>
      </div>
      <ActionBar
        previousTo="/inscription/preparation/siret"
        nextTo="/inscription/preparation/publics"
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorActivity
