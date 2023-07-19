import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CreateOffererQueryModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout/FormLayout'
import { getSirenDataAdapter } from 'core/Offerers/adapters'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import fullBackIcon from 'icons/full-back.svg'
import { ButtonLink, SirenInput, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Titles from 'ui-kit/Titles/Titles'

import styles from './OffererCreation.module.scss'
import OffererCreationUnavailable from './OffererCreationUnavailable/OffererCreationUnavailable'
import { validationSchema } from './validationSchema'

interface OffererCreationFormValues {
  siren: string
}

const OffererCreation = (): JSX.Element => {
  const isEntrepriseApiDisabled = useActiveFeature('DISABLE_ENTERPRISE_API')
  const navigate = useNavigate()
  const notification = useNotification()
  const [offerer, setOfferer] = useState<CreateOffererQueryModel>()
  const initialValues = { siren: '' }

  const redirectAfterSubmit = (createdOffererId: string) => {
    navigate(`/accueil?structure=${createdOffererId}`, { replace: true })
  }

  const handleSubmit = async (formValues: OffererCreationFormValues) => {
    try {
      const response = await getSirenDataAdapter(formValues.siren)

      if (!response.payload.values?.address) {
        notification.error('Impossible de vérifier le SIREN saisi.')
      } else {
        const createdOfferer = await api.createOfferer({
          ...response.payload.values,
          siren: formValues.siren?.replace(/\s/g, ''),
        })
        redirectAfterSubmit(createdOfferer.id.toString())
      }
    } catch (error) {
      notification.error('Vous étes déjà rattaché à cette structure.')
    }
  }

  const getSirenAPIData = async (siren: string) => {
    const response = await getSirenDataAdapter(siren)
    if (response.isOk) {
      setOfferer(response.payload.values)
    }
  }

  const formik = useFormik<OffererCreationFormValues>({
    initialValues,
    validationSchema,
    onSubmit: handleSubmit,
  })

  return (
    <div className={styles['offerer-page']}>
      <ButtonLink
        link={{ to: '/accueil', isExternal: false }}
        variant={ButtonVariant.TERNARY}
        icon={fullBackIcon}
        className={styles['offerer-page-go-back-link']}
      >
        Accueil
      </ButtonLink>
      <Titles title="Structure" />
      {isEntrepriseApiDisabled ? (
        <OffererCreationUnavailable />
      ) : (
        <FormikProvider value={formik}>
          <form onSubmit={formik.handleSubmit}>
            <FormLayout.Row>
              <SirenInput label="SIREN" onValidSiren={getSirenAPIData} />
            </FormLayout.Row>
            <FormLayout.Row>
              <div className={styles['op-detail-creation-form']}>
                <span>Siège social : </span>
                {offerer?.postalCode && (
                  <span>
                    {`${offerer?.address} - ${offerer?.postalCode} ${offerer?.city}`}
                  </span>
                )}
              </div>
            </FormLayout.Row>
            <FormLayout.Row>
              <div className={styles['op-detail-creation-form']}>
                <span>Désignation : </span>
                {offerer?.name && <span>{offerer?.name}</span>}
              </div>
            </FormLayout.Row>
            <div className={styles['offerer-form-validation']}>
              <div>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to: '/accueil',
                    isExternal: false,
                  }}
                >
                  Retour
                </ButtonLink>
              </div>
              <div>
                <SubmitButton variant={ButtonVariant.PRIMARY}>
                  Créer
                </SubmitButton>
              </div>
            </div>
          </form>
        </FormikProvider>
      )}
    </div>
  )
}

export default OffererCreation
