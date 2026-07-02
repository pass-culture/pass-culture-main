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
  tryRestoreTargetCustomerFromStorage,
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
  ImportanceLevelMessageSignupSimulation,
  OffererTarget,
  type SignupSimulationMessages,
  type SignupSimulationResponseModel,
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
    targetCustomer,
    setTargetCustomer,
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
      const finalTargetCustomer =
        targetCustomer ?? tryRestoreTargetCustomerFromStorage(setTargetCustomer)
      if (
        !finalActivity ||
        !finalOpenToPublic ||
        !finalSiret ||
        !finalTargetCustomer
      ) {
        return
      }

      const simulationResponse = await api.signupSimulation({
        body: {
          activity: finalActivity,
          isOpenToPublic: finalOpenToPublic === 'true',
          siret: finalSiret.replaceAll(' ', '') ?? '',
          targets: finalTargetCustomer?.individual
            ? finalTargetCustomer?.educational
              ? [OffererTarget.INDIVIDUAL, OffererTarget.COLLECTIVE]
              : [OffererTarget.INDIVIDUAL]
            : [OffererTarget.COLLECTIVE],
        },
      })
      setResult(simulationResponse)
    }
    doCall()
  }, [openToPublic, activity, siret, targetCustomer])

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
        {result?.messages.map((message: SignupSimulationMessages) => {
          const content = getAlertContent(message.content)
          return (
            <Banner
              title={content.title}
              key={message.content}
              variant={
                message.importanceLevel ===
                ImportanceLevelMessageSignupSimulation.ALERT
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
