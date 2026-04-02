import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'
import { ActionBar } from '@/pages/Simulator/components/ActionBar/ActionBar'

export const SimulatorResults = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Voici les justificatifs à préparer pour votre inscription
        </h1>
      </div>
      <ActionBar
        previousTo="/inscription/preparation/publics"
        nextTo="/inscription/compte/creation"
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorResults
