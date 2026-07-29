import { Banner, BannerVariants } from 'design-system/Banner/Banner'
import { useSimulatorContext } from 'pages/Simulator/SimulatorContext'
import {
  getAlertContent,
  getDocumentCardContent,
} from 'pages/Simulator/SimulatorResults/utils'
import {
  tryRestoreActivityFromStorage,
  tryRestoreOpenToPublicFromStorage,
  tryRestoreSiretFromStorage,
  tryRestoreTargetAudienceFromStorage,
} from 'pages/Simulator/storage'
import { useEffect, useState } from 'react'
import { InfoPanel } from 'ui-kit/InfoPanel/InfoPanel'
import { InfoPanelSize, InfoPanelSurface } from 'ui-kit/InfoPanel/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

import { api } from 'apiClient/api'
import {
  type ActivityNotOpenToPublic,
  type ActivityOpenToPublic,
  SignupSimulationMessageLevel,
  type SignupSimulationMessageModel,
  type SignupSimulationResponseModel,
  TargetAudience,
} from 'apiClient/v1'
import styles from './SimulatorResults.module.scss'

export const SimulatorResults = (): JSX.Element => {
  const {
    openToPublic,
    setOpenToPublic,
    activity,
    setActivity,
    siret,
    setSiret,
    targetAudiences,
    setTargetAudiences,
  } = useSimulatorContext()

  const [result, setResult] = useState<
    SignupSimulationResponseModel | undefined
  >()

  useEffect(() => {
    const doCall = async () => {
      const finalOpenToPublic =
        openToPublic ?? tryRestoreOpenToPublicFromStorage(setOpenToPublic)
      const finalActivity =
        (activity as ActivityOpenToPublic | ActivityNotOpenToPublic) ||
        tryRestoreActivityFromStorage(setActivity)
      const finalSiret = siret ?? tryRestoreSiretFromStorage(setSiret)
      const finalTargetAudience =
        targetAudiences?.individual !== undefined
          ? targetAudiences
          : tryRestoreTargetAudienceFromStorage(setTargetAudiences)

      const targets = []
      if (finalTargetAudience?.individual) {
        targets.push(TargetAudience.INDIVIDUAL)
      }
      if (finalTargetAudience?.collective) {
        targets.push(TargetAudience.COLLECTIVE)
      }

      if (
        !finalActivity ||
        !finalOpenToPublic ||
        !finalSiret ||
        targets.length === 0
      ) {
        return
      }

      const simulationResponse = await api.simulateSignup({
        body: {
          activity: finalActivity,
          isOpenToPublic: finalOpenToPublic === 'true',
          siret: finalSiret.replaceAll(' ', '') ?? '',
          targets,
        },
      })
      setResult(simulationResponse)
    }
    doCall()
  }, [
    activity,
    openToPublic,
    setActivity,
    setOpenToPublic,
    setSiret,
    setTargetAudiences,
    siret,
    targetAudiences,
  ])

  if (!result) {
    return <Spinner />
  }

  return (
    <>
      <div className={commonStyles['content']}>
        <h1 className={commonStyles['title']}>
          Voici les justificatifs à préparer pour votre inscription
        </h1>
      </div>
      <div className={styles['documents']}>
        {result?.eligibilityDocuments.map((document, index: number) => {
          const { title, description } = getDocumentCardContent(document)
          return (
            <InfoPanel
              surface={InfoPanelSurface.ELEVATED}
              size={InfoPanelSize.SMALL}
              title={title}
              stepNumber={index + 1}
              key={title}
              titleLevel="2"
            >
              {description}
            </InfoPanel>
          )
        })}
        {result?.messages.map((message: SignupSimulationMessageModel) => {
          const content = getAlertContent(message.type)
          return (
            <Banner
              title={content.title}
              key={message.type}
              variant={
                message.level === SignupSimulationMessageLevel.ALERT
                  ? BannerVariants.WARNING
                  : BannerVariants.DEFAULT
              }
              actions={content.link}
              closable={false}
              description={content.description}
            />
          )
        })}
      </div>
      <div className={commonStyles['action-bar']}>
        <Button
          as="router-link"
          to="/inscription/preparation/publics"
          variant={ButtonVariant.SECONDARY}
          label="Retour"
        />
        <Button as="router-link" to="/inscription/compte/creation" label="Continuer" />
      </div>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorResults
