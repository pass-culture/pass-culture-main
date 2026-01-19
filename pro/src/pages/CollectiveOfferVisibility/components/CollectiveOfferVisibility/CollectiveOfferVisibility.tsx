import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect, useMemo, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import useSWR from 'swr'
import { useDebouncedCallback } from 'use-debounce'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import {
  CollectiveOfferAllowedAction,
  type EducationalInstitutionResponseModel,
  type EducationalRedactor,
  type GetCollectiveOfferResponseModel,
  type PatchCollectiveOfferEducationalInstitution,
} from '@/apiClient/v1'
import {
  GET_AUTOCOMPLETE_EDUCATIONAL_REDACTORS_FOR_UAI_KEY,
  GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { isCollectiveOffer, Mode } from '@/commons/core/OfferEducational/types'
import {
  extractInitialVisibilityValues,
  formatInstitutionDisplayName,
} from '@/commons/core/OfferEducational/utils/extractInitialVisibilityValues'
import {
  GET_DATA_ERROR_MESSAGE,
  SENT_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { searchPatternInOptions } from '@/commons/utils/searchPatternInOptions'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from '@/components/BannerPublicApi/BannerPublicApi'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { SelectAutocomplete } from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import {
  DEFAULT_FORM_FIELD_ERRORS,
  FORM_KEYS_MAPPING,
  GET_REDACTOR_NOT_FOUND_ERROR_MESSAGE,
  INSTITUTION_GENERIC_ERROR_MESSAGE,
  POST_VISIBILITY_FORM_ERROR_MESSAGE,
  REDACTOR_GENERIC_ERROR_MESSAGE,
} from '../../commons/constants'
import {
  type VisibilityFormValues,
  validationSchema,
} from '../../commons/validationSchema'
import styles from './CollectiveOfferVisibility.module.scss'

export interface CollectiveOfferVisibilityProps {
  mode: Mode
  initialValues: VisibilityFormValues
  onSuccess: ({
    offerId,
    message,
    payload,
  }: {
    offerId: string
    message: string
    payload: GetCollectiveOfferResponseModel
  }) => void
  institutions: EducationalInstitutionResponseModel[]
  isLoadingInstitutions: boolean
  offer: GetCollectiveOfferResponseModel
  requestId?: string | null
}
interface InstitutionOption extends SelectOption {
  institutionId: string
}

interface TeacherOption extends SelectOption {
  surname?: string | null
  name: string
  gender?: string | null
  email: string
}

export const CollectiveOfferVisibilityScreen = ({
  mode,
  initialValues,
  onSuccess,
  institutions,
  isLoadingInstitutions,
  offer,
  requestId = '',
}: CollectiveOfferVisibilityProps) => {
  const snackBar = useSnackBar()

  const [teachersOptions, setTeachersOptions] = useState<TeacherOption[]>([])

  const canEditInstitution = isActionAllowedOnCollectiveOffer(
    offer,
    CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION
  )

  const institutionsOptions: InstitutionOption[] = useMemo(
    () =>
      institutions.map(
        ({ name, id, city, postalCode, institutionType, institutionId }) => {
          const label = formatInstitutionDisplayName({
            name,
            institutionType: institutionType || '',
            institutionId,
            city,
            postalCode,
          })
          return {
            label: label,
            value: String(id),
            institutionId: institutionId,
          }
        }
      ),
    [institutions]
  )

  const { data: requestInformations } = useSWR(
    () =>
      requestId
        ? [GET_COLLECTIVE_REQUEST_INFORMATIONS_QUERY_KEY, requestId]
        : null,
    ([, id]) => api.getCollectiveOfferRequest(Number(id))
  )

  const manualFormValidation = (
    body: PatchCollectiveOfferEducationalInstitution
  ) => {
    if (!body.educationalInstitutionId) {
      form.setError('institution', {
        message: INSTITUTION_GENERIC_ERROR_MESSAGE,
      })
      return false
    }
    if (watch('teacher') && !body.teacherEmail) {
      form.setError('teacher', {
        message: REDACTOR_GENERIC_ERROR_MESSAGE,
      })
      return false
    }
    return true
  }

  const onSubmit = async (values: VisibilityFormValues) => {
    const selectedTeacher: TeacherOption | null = requestId
      ? teachersOptions[0]
      : (teachersOptions.find(
          (teacher) => teacher.value === watch('teacher')
        ) ?? null)
    const teacherEmail = selectedTeacher ? selectedTeacher.email : null

    const isValid = manualFormValidation({
      educationalInstitutionId: Number(values.institution),
      teacherEmail,
    })
    if (!isValid) {
      return
    }

    try {
      const collectiveOffer =
        await api.patchCollectiveOffersEducationalInstitution(offer.id, {
          educationalInstitutionId: Number(values.institution),
          teacherEmail: teacherEmail,
        })

      onSuccess({
        offerId: offer.id.toString(),
        message:
          'Les paramètres de visibilité de votre offre ont bien été enregistrés',
        payload: collectiveOffer,
      })

      reset({
        ...extractInitialVisibilityValues(collectiveOffer.institution),
      })
    } catch (error) {
      if (isErrorAPIError(error)) {
        const serializedApiErrors = serializeApiErrors(
          error.body,
          FORM_KEYS_MAPPING
        )

        snackBar.error(POST_VISIBILITY_FORM_ERROR_MESSAGE)

        Object.entries(serializedApiErrors).forEach(([field]) => {
          form.setError(field as keyof VisibilityFormValues, {
            message:
              DEFAULT_FORM_FIELD_ERRORS[field as keyof VisibilityFormValues] ||
              SENT_DATA_ERROR_MESSAGE,
          })
        })
      } else {
        snackBar.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  initialValues = requestInformations
    ? {
        ...extractInitialVisibilityValues(null, null, requestInformations),
        institution:
          institutionsOptions
            .find(
              (option) =>
                option.institutionId ===
                requestInformations.institution.institutionId
            )
            ?.value.toString() || '',
      }
    : initialValues

  const form = useForm<VisibilityFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver<VisibilityFormValues, unknown, unknown>(
      validationSchema
    ),
    mode: 'onBlur',
  })

  const {
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { isDirty, isSubmitting, errors },
  } = form

  const institution = watch('institution')
  const selectedInstitution = institutionsOptions.find(
    (_institution) => _institution.value === institution
  )

  const teacher = watch('teacher')
  const selectedTeacher = teachersOptions.find(
    (_teacher) => _teacher.value === teacher
  )

  const { isLoading: isPreloadingRedactors } = useSWR(
    () =>
      selectedInstitution?.institutionId
        ? [
            GET_AUTOCOMPLETE_EDUCATIONAL_REDACTORS_FOR_UAI_KEY,
            selectedInstitution?.institutionId,
          ]
        : null,
    async ([, institutionUai]) => {
      try {
        if (institutionUai) {
          await api.getAutocompleteEducationalRedactorsForUai(
            institutionUai,
            'preload'
          )
        }
      } catch (error) {
        if (isErrorAPIError(error) && error.status === 404) {
          console.warn('No redactors found')
        } else {
          snackBar.error(GET_DATA_ERROR_MESSAGE)
        }
      }
    }
  )

  useEffect(() => {
    if (!requestInformations) {
      return
    }

    const institutionOption = institutionsOptions.find(
      (opt) =>
        opt.institutionId === requestInformations.institution.institutionId
    )

    const formValues: VisibilityFormValues = {
      ...extractInitialVisibilityValues(null, null, requestInformations),
      institution: institutionOption?.value.toString() ?? '',
      teacher: requestInformations.redactor.email,
    }

    reset(formValues)

    const { firstName, lastName, email } = requestInformations.redactor
    setTeachersOptions([
      {
        label: `${lastName ?? ''} ${firstName ?? ''}`.trim(),
        value: email,
        surname: lastName ?? '',
        name: firstName ?? '',
        email,
      },
    ])
  }, [requestInformations, institutionsOptions, reset])

  const onSearchTeacher = useDebouncedCallback(async (pattern: string) => {
    const selectedInstitution = institutionsOptions.find(
      (institution) => institution.value === watch('institution')
    )

    const searchTeacherValue = pattern.trim()

    if (
      !searchTeacherValue ||
      searchTeacherValue.length < 3 ||
      !selectedInstitution
    ) {
      setTeachersOptions([])
      return
    }

    try {
      const payload = await api.getAutocompleteEducationalRedactorsForUai(
        selectedInstitution.institutionId,
        searchTeacherValue
      )
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
    } catch {
      form.setError('teacher', {
        message: GET_REDACTOR_NOT_FOUND_ERROR_MESSAGE,
      })
    }
  }, 400)

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        offer={offer}
        mode={mode}
      />

      <FormProvider {...form}>
        <div className={styles.container}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <FormLayout>
              {isCollectiveOffer(offer) && offer.isPublicApi && (
                <BannerPublicApi className={styles['banner-space']} />
              )}
              <FormLayout.Section title="Renseignez l'établissement scolaire et l'enseignant">
                <p className={styles['description-text']}>
                  L’établissement et l’enseignant renseignés sont les seuls à
                  pouvoir visualiser et préréserver votre offre sur ADAGE.
                </p>
                <FormLayout.Row className={styles['row-layout']} mdSpaceAfter>
                  {isLoadingInstitutions ? (
                    <Spinner />
                  ) : (
                    <SelectAutocomplete
                      name="institution"
                      options={institutionsOptions}
                      label="Nom de l’établissement scolaire ou code UAI"
                      description="Ex : Lycee General Simone Weil ou 010456E ou Le Havre"
                      shouldResetOnOpen={true}
                      onSearch={(searchText) => {
                        setValue('institution', searchText, {
                          shouldDirty: true,
                          shouldValidate: true,
                        })
                      }}
                      onChange={(event) => {
                        setValue('institution', event.target.value, {
                          shouldDirty: true,
                          shouldValidate: true,
                        })

                        setValue('teacher', '')
                      }}
                      disabled={!canEditInstitution}
                      searchInOptions={(options, pattern) =>
                        searchPatternInOptions(options, pattern, 300)
                      }
                      value={selectedInstitution?.value ?? ''}
                      error={errors.institution?.message}
                      required
                      requiredIndicator="explicit"
                    />
                  )}
                </FormLayout.Row>
                <FormLayout.Row className={styles['row-layout']}>
                  <SelectAutocomplete
                    name="teacher"
                    options={teachersOptions}
                    label="Prénom et nom de l’enseignant (au moins 3 caractères)"
                    required={false}
                    description="Ex: Camille Dupont"
                    shouldResetOnOpen={true}
                    onSearch={(searchText) => {
                      setValue('teacher', searchText, {
                        shouldDirty: true,
                        shouldValidate: true,
                      })
                      onSearchTeacher(searchText)
                    }}
                    disabled={
                      !canEditInstitution ||
                      !watch('institution') ||
                      isPreloadingRedactors
                    }
                    onChange={(event) => {
                      setValue('teacher', event.target.value, {
                        shouldDirty: true,
                        shouldValidate: true,
                      })
                    }}
                    value={selectedTeacher?.value || watch('teacher')}
                    error={errors.teacher?.message}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
              <ActionsBarSticky>
                <ActionsBarSticky.Left>
                  <Button
                    as="a"
                    variant={ButtonVariant.SECONDARY}
                    color={
                      mode === Mode.CREATION
                        ? ButtonColor.BRAND
                        : ButtonColor.NEUTRAL
                    }
                    to={
                      mode === Mode.CREATION
                        ? `/offre/${offer.id}/collectif/stocks${
                            requestId ? `?requete=${requestId}` : ''
                          }`
                        : '/offres/collectives'
                    }
                    label={
                      mode === Mode.CREATION ? 'Retour' : 'Annuler et quitter'
                    }
                  />
                </ActionsBarSticky.Left>
                <ActionsBarSticky.Right dirtyForm={isDirty} mode={mode}>
                  <Button
                    type="submit"
                    disabled={!watch('institution') || !canEditInstitution}
                    label="Enregistrer et continuer"
                  />
                </ActionsBarSticky.Right>
              </ActionsBarSticky>
            </FormLayout>
          </form>
        </div>
      </FormProvider>
      <RouteLeavingGuardCollectiveOfferCreation
        when={isDirty && !isSubmitting}
      />
    </>
  )
}
