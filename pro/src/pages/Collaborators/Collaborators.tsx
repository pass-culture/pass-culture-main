import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import classNames from 'classnames'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { OffererMemberStatus } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_MEMBERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { OffererLinkEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureOffererNamesValidated } from '@/commons/store/offerer/selectors'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullDownIcon from '@/icons/full-down.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { validationSchema } from '@/pages/Collaborators/validationSchema'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import styles from './Collaborators.module.scss'

const SUCCESS_MESSAGE = "L'invitation a bien été envoyée."
const ERROR_MESSAGE = 'Une erreur est survenue lors de l’envoi de l’invitation.'

type UserEmailFormValues = {
  email: string
}

const Collaborators = () => {
  const { logEvent } = useAnalytics()
  const snackBar = useSnackBar()
  const [displayAllMembers, setDisplayAllMembers] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  const offererId = selectedAdminOfferer.id

  const offererNamesValidated = useAppSelector(ensureOffererNamesValidated)
  const isSelectedOffererValidated = offererNamesValidated.some(
    (offerer) => offerer.id === offererId
  )

  const { data } = useSWR(
    [GET_MEMBERS_QUERY_KEY, offererId],
    ([, offererIdParam]) =>
      !offererIdParam || !isSelectedOffererValidated
        ? null
        : api.getOffererMembers(offererIdParam),
    { fallbackData: null }
  )
  const members = data?.members ?? []

  const hookForm = useForm<UserEmailFormValues>({
    defaultValues: { email: '' },
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = hookForm

  const onSubmit = async ({ email }: { email: string }) => {
    try {
      if (!offererId) {
        return
      }

      await api.inviteMember(offererId, { email: email })

      members.unshift({
        email,
        status: OffererMemberStatus.PENDING,
      })
      reset()
      logEvent(OffererLinkEvents.CLICKED_SEND_INVITATION, {
        offererId: offererId,
      })
      snackBar.success(SUCCESS_MESSAGE)
      setIsDialogOpen(false)
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400 && error.body.email) {
        setError('email', { message: error.body.email })
      } else {
        snackBar.error(ERROR_MESSAGE)
      }
    }
  }

  const MAX_COLLABORATORS = 10

  return (
    <>
      {isSelectedOffererValidated && (
        <section>
          <h2 className={styles['main-list-title']}>
            Liste des collaborateurs
          </h2>

          {members.length > 0 && (
            <div className={styles['members-container']}>
              <table
                className={classNames(styles['members-list'], {
                  [styles['members-list--withMarginBottom']]:
                    members.length > MAX_COLLABORATORS,
                })}
              >
                <thead>
                  <tr className={styles['members-list-tr']}>
                    <th scope="col" className={styles['members-list-th']}>
                      Email
                    </th>
                    <th scope="col" className={styles['members-list-th']}>
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {members.map(
                    ({ email, status }, index) =>
                      !(
                        !displayAllMembers && index > MAX_COLLABORATORS - 1
                      ) && (
                        <tr key={email} className={styles['members-list-tr']}>
                          <td
                            className={classNames(
                              styles['member-email'],
                              styles['members-list-td']
                            )}
                          >
                            {email}
                          </td>
                          <td
                            className={classNames(
                              styles['member-status'],
                              styles['members-list-td']
                            )}
                          >
                            {status === OffererMemberStatus.VALIDATED ? (
                              <Tag
                                variant={TagVariant.SUCCESS}
                                label="Validé"
                              />
                            ) : (
                              <Tag
                                variant={TagVariant.DEFAULT}
                                label="En attente"
                              />
                            )}
                          </td>
                        </tr>
                      )
                  )}
                </tbody>
              </table>

              {members.length > MAX_COLLABORATORS && (
                <Button
                  onClick={() => setDisplayAllMembers(!displayAllMembers)}
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  icon={displayAllMembers ? fullUpIcon : fullDownIcon}
                  label={
                    displayAllMembers
                      ? 'Voir moins de collaborateurs'
                      : 'Voir plus de collaborateurs'
                  }
                />
              )}
            </div>
          )}

          <DialogBuilder
            variant="drawer"
            title="Ajout de collaborateurs"
            open={isDialogOpen}
            onOpenChange={setIsDialogOpen}
            trigger={
              <Button
                variant={ButtonVariant.PRIMARY}
                onClick={() => {
                  logEvent(OffererLinkEvents.CLICKED_ADD_COLLABORATOR, {
                    offererId: offererId,
                  })
                }}
                label="Ajouter un collaborateur"
              />
            }
          >
            <form
              className={styles['invitation-form']}
              onSubmit={handleSubmit(onSubmit)}
            >
              <div className={styles['invitation-form']}>
                <p className={styles['description']}>
                  Vous pouvez inviter des collaborateurs à rejoindre votre
                  espace. Une invitation leur sera envoyée par email. Vous serez
                  notifié quand ils auront rejoint l’espace.
                </p>

                <FormLayout>
                  <FormLayout.Row>
                    <TextInput
                      label="Adresse email"
                      type="email"
                      description="Format : email@exemple.com"
                      error={errors.email?.message}
                      required
                      requiredIndicator="explicit"
                      {...register('email')}
                    />
                  </FormLayout.Row>
                </FormLayout>
              </div>

              <DialogBuilder.Footer>
                <div className={styles['action-buttons']}>
                  <Dialog.Close asChild>
                    <Button
                      variant={ButtonVariant.SECONDARY}
                      color={ButtonColor.NEUTRAL}
                      label="Annuler"
                    />
                  </Dialog.Close>
                  <Button
                    type="submit"
                    isLoading={isSubmitting}
                    data-error={errors.email?.message ? 'true' : 'false'}
                    label="Inviter le collaborateur"
                  />
                </div>
              </DialogBuilder.Footer>
            </form>
          </DialogBuilder>
        </section>
      )}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Collaborators
