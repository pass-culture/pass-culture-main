import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'
import { ActionBar } from '@/pages/Simulator/components/ActionBar/ActionBar'

export const SimulatorSiret = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>Renseignez votre SIRET</h1>
      </div>
      <ActionBar
        previousTo="/bienvenue/prochaines-etapes"
        nextTo="/inscription/preparation/activite"
      />
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorSiret
