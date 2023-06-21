import { FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  EducationalInstitutionResponseModel,
  EducationalRedactor,
  GetCollectiveOfferRequestResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import BannerPublicApi from 'components/Banner/BannerPublicApi'
import FormLayout from 'components/FormLayout'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  CollectiveOffer,
  isCollectiveOffer,
  Mode,
  VisibilityFormValues,
} from 'core/OfferEducational'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import { TrashFilledIcon } from 'icons'
import getOfferRequestInformationsAdapter from 'pages/CollectiveOfferFromRequest/adapters/getOfferRequestInformationsAdapter'
import { PatchEducationalInstitutionAdapter } from 'pages/CollectiveOfferVisibility/adapters/patchEducationalInstitutionAdapter'
import {
  Banner,
  Button,
  ButtonLink,
  SelectAutocomplete,
  SubmitButton,
} from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import RadioGroup from 'ui-kit/form/RadioGroup'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import getEducationalRedactorsAdapter from './adapters/getEducationalRedactorAdapter'
import styles from './CollectiveOfferVisibility.module.scss'
import validationSchema from './validationSchema'

export interface CollectiveOfferVisibilityProps {
  patchInstitution: PatchEducationalInstitutionAdapter
  mode: Mode
  initialValues: VisibilityFormValues
  onSuccess: ({
    offerId,
    message,
    payload,
  }: {
    offerId: string
    message: string
    payload: CollectiveOffer
  }) => void
  institutions: EducationalInstitutionResponseModel[]
  isLoadingInstitutions: boolean
  offer: CollectiveOffer
  reloadCollectiveOffer?: () => void
  requestId?: string | null
}
interface InstitutionOption extends SelectOption {
  postalCode?: string
  city?: string
  name: string
  institutionType?: string
  institutionId: string
}

interface TeacherOption extends SelectOption {
  surname: string
  name: string
  gender: string
  email: string
}

const CollectiveOfferVisibility = ({
  mode,
  patchInstitution,
  initialValues,
  onSuccess,
  institutions,
  isLoadingInstitutions,
  offer,
  reloadCollectiveOffer,
  requestId = '',
}: CollectiveOfferVisibilityProps) => {
  const notify = useNotification()

  const [teachersOptions, setTeachersOptions] = useState<TeacherOption[]>([])
  const [buttonPressed, setButtonPressed] = useState(false)
  const [requestInformations, setRequestInformations] =
    useState<GetCollectiveOfferRequestResponseModel | null>(null)

  const getOfferRequestInformation = async () => {
    const { isOk, message, payload } = await getOfferRequestInformationsAdapter(
      Number(requestId)
    )

    if (!isOk) {
      return notify.error(message)
    }

    setRequestInformations(payload)
  }

  useEffect(() => {
    requestId && getOfferRequestInformation()
  }, [])

  const onSubmit = async (values: VisibilityFormValues) => {
    setButtonPressed(true)
    const result = await patchInstitution({
      offerId: offer.nonHumanizedId,
      institutionId: values.visibility === 'all' ? null : values.institution,
      teacherEmail: selectedTeacher ? selectedTeacher.email : null,
    })
    if (!result.isOk) {
      setButtonPressed(false)
      return notify.error(result.message)
    }
    onSuccess({
      offerId: offer.id,
      message: result.message ?? '',
      payload: result.payload,
    })
    setButtonPressed(false)
    formik.resetForm({
      values: extractInitialVisibilityValues(result.payload.institution),
    })
  }

  initialValues = requestId
    ? extractInitialVisibilityValues(null, null, requestInformations)
    : initialValues

  const formik = useFormik<VisibilityFormValues>({
    initialValues,
    onSubmit,
    validationSchema,
    enableReinitialize: true,
  })

  const selectedTeacher: TeacherOption | null = requestId
    ? teachersOptions[0]
    : teachersOptions?.find(
        teacher => teacher.value === formik.values.teacher
      ) ?? null

  const institutionsOptions: InstitutionOption[] = institutions
    .map(({ name, id, city, postalCode, institutionType, institutionId }) => ({
      label: `${
        institutionType ?? ''
      } ${name} - ${city} - ${institutionId}`.trim(),
      value: String(id),
      city,
      postalCode,
      name,
      institutionType: institutionType ?? '',
      institutionId: institutionId,
    }))
    .filter(({ label }) =>
      label
        .toLowerCase()
        .includes(formik.values['search-institution'].toLowerCase())
    )

  const selectedInstitution: InstitutionOption | null = requestId
    ? institutionsOptions[0]
    : institutionsOptions?.find(
        institution => institution?.value === formik.values.institution
      ) ?? null

  const onChangeTeacher = async () => {
    if (requestId) {
      formik.setFieldValue('institution', selectedInstitution?.value)
    }
    if (
      !(
        formik.values['search-teacher'] &&
        formik.values['search-teacher'].length > 2
      ) ||
      !selectedInstitution
    ) {
      return
    }
    const { payload } = await getEducationalRedactorsAdapter({
      uai: selectedInstitution?.institutionId,
      candidate: formik.values['search-teacher'],
    })
    payload &&
      setTeachersOptions(
        payload.map(
          ({
            name,
            surname,
            gender,
            email,
          }: EducationalRedactor): TeacherOption => ({
            label: `${surname} ${name}`.trim(),
            value: email,
            surname,
            name,
            gender,
            email,
          })
        )
      )
  }

  const clearAllFields = () => {
    formik.setFieldValue('search-institution', '')
    formik.setFieldValue('institution', '')
    formik.setFieldValue('search-teacher', '')
    formik.setFieldValue('teacher', '')
  }
  const noInstitutionSelected =
    formik.values.visibility === 'one' && formik.values.institution.length === 0
  const nextStepDisabled =
    buttonPressed || noInstitutionSelected || mode === Mode.READ_ONLY

  return (
    <>
      <OfferEducationalActions
        reloadCollectiveOffer={reloadCollectiveOffer}
        className={styles.actions}
        isBooked={Boolean(offer.collectiveStock?.isBooked)}
        offer={offer}
        mode={mode}
      />
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <FormLayout>
            {isCollectiveOffer(offer) && offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']}>
                Offre importée automatiquement
              </BannerPublicApi>
            )}
            <FormLayout.Section title="Visibilité de l’offre">
              <p className={styles['description-text']}>
                Les établissements concernés par vos choix seront les seuls à
                pouvoir visualiser et/ou préréserver votre offre sur ADAGE. Vous
                avez jusqu’à la préréservation d’un enseignant pour modifier la
                visibilité de votre offre.
              </p>
              <FormLayout.Row className={styles['row-layout']}>
                <fieldset className={styles['legend']}>
                  Quel établissement scolaire peut voir votre offre ?
                </fieldset>
                <RadioGroup
                  className={styles['radio-group']}
                  disabled={mode === Mode.READ_ONLY}
                  variant={BaseRadioVariant.SECONDARY}
                  group={[
                    {
                      label: 'Un établissement en particulier',
                      value: 'one',
                    },
                    {
                      label: 'Tous les établissements',
                      value: 'all',
                    },
                  ]}
                  name="visibility"
                  withBorder
                />
              </FormLayout.Row>
              {institutionsOptions && formik.values.visibility === 'one' && (
                <FormLayout.Row className={styles['row-layout']}>
                  {isLoadingInstitutions ? (
                    <Spinner />
                  ) : (
                    <>
                      <SelectAutocomplete
                        name="institution"
                        options={institutionsOptions}
                        label="Nom de l’établissement scolaire"
                        placeholder="Saisir l’établissement scolaire ou le code UAI"
                        maxDisplayOptions={20}
                        maxDisplayOptionsLabel="20 résultats maximum. Veuillez affiner votre recherche"
                        maxHeight={100}
                        hideArrow
                        onSearchChange={() => setTeachersOptions([])}
                        disabled={mode === Mode.READ_ONLY}
                      />
                      {selectedInstitution && (
                        <Banner type="light" className={styles['institution']}>
                          <div className={styles['banner-with-bin']}>
                            <div>
                              {`${selectedInstitution.institutionType} ${selectedInstitution.name}`.trim()}
                              <br />
                              {`${selectedInstitution.postalCode} ${selectedInstitution.city}`}
                              <br />
                              {selectedInstitution.institutionId}
                            </div>
                            <Button
                              variant={ButtonVariant.TERNARY}
                              onClick={() => clearAllFields()}
                              Icon={TrashFilledIcon}
                              iconPosition={IconPositionEnum.CENTER}
                              hasTooltip
                            >
                              Supprimer
                            </Button>
                          </div>
                        </Banner>
                      )}
                    </>
                  )}
                </FormLayout.Row>
              )}
              {formik.values.visibility === 'one' && selectedInstitution && (
                <FormLayout.Row className={styles['row-layout']}>
                  <fieldset className={styles['legend']}>
                    À quel enseignant destinez-vous cette offre ?
                  </fieldset>
                  <>
                    <SelectAutocomplete
                      name="teacher"
                      options={teachersOptions}
                      label="Prénom et nom de l’enseignant (au moins 3 caractères)"
                      isOptional
                      placeholder="Saisir le prénom et le nom de l’enseignant"
                      maxDisplayOptions={5}
                      maxDisplayOptionsLabel="5 résultats maximum. Veuillez affiner votre recherche"
                      maxHeight={190}
                      hideArrow
                      disabled={mode === Mode.READ_ONLY}
                      onSearchChange={() => {
                        onChangeTeacher()
                      }}
                    />
                    {selectedTeacher && (
                      <Banner type="light" className={styles['institution']}>
                        <div className={styles['banner-with-bin']}>
                          <div>
                            {`${selectedTeacher.surname} ${selectedTeacher.name}`.trim()}
                          </div>
                          <Button
                            variant={ButtonVariant.TERNARY}
                            onClick={() => {
                              formik.setFieldValue('search-teacher', '')
                              formik.setFieldValue('teacher', null)
                            }}
                            Icon={TrashFilledIcon}
                            iconPosition={IconPositionEnum.CENTER}
                            hasTooltip
                          >
                            Supprimer
                          </Button>
                        </div>
                      </Banner>
                    )}
                  </>
                </FormLayout.Row>
              )}
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to: `/offre/${offer.id}/collectif/stocks${
                      requestId ? `?requete=${requestId}` : ''
                    }`,
                    isExternal: false,
                  }}
                >
                  Étape précédente
                </ButtonLink>
              </ActionsBarSticky.Left>
              <ActionsBarSticky.Right>
                <SubmitButton disabled={nextStepDisabled} isLoading={false}>
                  {mode === Mode.CREATION
                    ? 'Étape suivante'
                    : 'Valider et enregistrer l’offre'}
                </SubmitButton>
              </ActionsBarSticky.Right>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormikProvider>
    </>
  )
}

export default CollectiveOfferVisibility
