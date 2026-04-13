import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

export const SimulatorResults = (): JSX.Element => {
  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Voici les justificatifs à préparer pour votre inscription
        </h1>
      </div>
      <div className={commonStyles['action-bar']}>
        <Button
          as="a"
          to="/inscription/preparation/publics"
          variant={ButtonVariant.SECONDARY}
          label="Retour"
        />
        <Button as="a" to="/inscription/compte/creation" label="Continuer" />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorResults
