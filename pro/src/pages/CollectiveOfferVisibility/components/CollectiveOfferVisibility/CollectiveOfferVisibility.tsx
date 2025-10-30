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
import { useNotification } from '@/commons/hooks/useNotification'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import {
  normalizeStrForSearch,
  type SelectOptionNormalized,
  searchPatternInOptions,
} from '@/commons/utils/searchPatternInOptions'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { BannerPublicApi } from '@/components/BannerPublicApi/BannerPublicApi'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OfferEducationalActions } from '@/components/OfferEducationalActions/OfferEducationalActions'
import { RouteLeavingGuardCollectiveOfferCreation } from '@/components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
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
interface InstitutionOption extends SelectOptionNormalized {
  postalCode?: string
  city?: string
  name: string
  institutionType?: string
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
  const notify = useNotification()

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
            normalizedLabel: normalizeStrForSearch(label),
            value: String(id),
            city,
            postalCode,
            name,
            institutionType: institutionType ?? '',
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

        notify.error(POST_VISIBILITY_FORM_ERROR_MESSAGE)

        Object.entries(serializedApiErrors).forEach(([field]) => {
          form.setError(field as keyof VisibilityFormValues, {
            message:
              DEFAULT_FORM_FIELD_ERRORS[field as keyof VisibilityFormValues] ||
              SENT_DATA_ERROR_MESSAGE,
          })
        })
      } else {
        notify.error(SENT_DATA_ERROR_MESSAGE)
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
          notify.error(GET_DATA_ERROR_MESSAGE)
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
      <FormLayout.MandatoryInfo />

      <OfferEducationalActions
        className={styles.actions}
        offer={offer}
        mode={mode}
      />

      <FormProvider {...form}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <FormLayout>
            {isCollectiveOffer(offer) && offer.isPublicApi && (
              <BannerPublicApi className={styles['banner-space']}>
                Offre importée automatiquement
              </BannerPublicApi>
            )}
            <FormLayout.Section title="Renseignez l'établissement scolaire et l'enseignant">
              <p className={styles['description-text']}>
                L’établissement et l’enseignant renseignés sont les seuls à
                pouvoir visualiser et préréserver votre offre sur ADAGE.
              </p>
              <FormLayout.Row className={styles['row-layout']}>
                {isLoadingInstitutions ? (
                  <Spinner />
                ) : (
                  <SelectAutocomplete
                    name="institution"
                    options={institutionsOptions}
                    label="Nom de l’établissement scolaire ou code UAI"
                    description="Ex : Lycee General Simone Weil ou 010456E ou Le Havre"
                    hideArrow
                    onReset={() => {
                      setValue('institution', '')
                      setValue('teacher', '')
                    }}
                    onChange={(event) => {
                      setValue('institution', event.target.value, {
                        shouldDirty: true,
                        shouldValidate: true,
                      })

                      setValue('teacher', undefined)
                    }}
                    disabled={!canEditInstitution}
                    searchInOptions={(options, pattern) =>
                      searchPatternInOptions(options, pattern, 300)
                    }
                    value={watch('institution')}
                    error={errors.institution?.message}
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
                  hideArrow
                  onReset={() => {
                    setValue('teacher', '')
                  }}
                  onSearch={onSearchTeacher}
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
                  value={watch('institution') ? watch('teacher') : undefined}
                  error={errors.teacher?.message}
                />
              </FormLayout.Row>
            </FormLayout.Section>
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  to={
                    mode === Mode.CREATION
                      ? `/offre/${offer.id}/collectif/stocks${
                          requestId ? `?requete=${requestId}` : ''
                        }`
                      : '/offres/collectives'
                  }
                >
                  {mode === Mode.CREATION ? 'Retour' : 'Annuler et quitter'}
                </ButtonLink>
              </ActionsBarSticky.Left>
              <ActionsBarSticky.Right dirtyForm={isDirty} mode={mode}>
                <Button
                  type="submit"
                  disabled={!watch('institution') || !canEditInstitution}
                >
                  Enregistrer et continuer
                </Button>
              </ActionsBarSticky.Right>
            </ActionsBarSticky>
          </FormLayout>
        </form>
      </FormProvider>
      <RouteLeavingGuardCollectiveOfferCreation
        when={isDirty && !isSubmitting}
      />
    </>
  )
}
