import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { CreateOffererQueryModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
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

export const OffererCreation = (): JSX.Element => {
  const isEntrepriseApiDisabled = useActiveFeature('DISABLE_ENTERPRISE_API')
  const navigate = useNavigate()
  const notification = useNotification()
  const [offerer, setOfferer] = useState<CreateOffererQueryModel>()
  const initialValues = { siren: '' }
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (formValues: OffererCreationFormValues) => {
    setIsSubmitting(true)
    try {
      const response = await getSirenDataAdapter(formValues.siren)

      if (!response.payload.values?.address) {
        notification.error('Impossible de vérifier le SIREN saisi.')
        setIsSubmitting(false)
      } else {
        const createdOfferer = await api.createOfferer({
          ...response.payload.values,
          siren: formValues.siren?.replace(/\s/g, ''),
        })
        navigate(`/accueil?structure=${createdOfferer.id}`, { replace: true })
      }
    } catch (error) {
      if (isErrorAPIError(error) && error.status == 400 && error.body.siren) {
        notification.error('Le code SIREN saisi n’est pas valide.')
      } else {
        notification.error('Vous êtes déjà rattaché à cette structure.')
      }
      setIsSubmitting(false)
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
    <AppLayout>
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
                  <SubmitButton
                    variant={ButtonVariant.PRIMARY}
                    disabled={isSubmitting}
                  >
                    Créer
                  </SubmitButton>
                </div>
              </div>
            </form>
          </FormikProvider>
        )}
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OffererCreation
