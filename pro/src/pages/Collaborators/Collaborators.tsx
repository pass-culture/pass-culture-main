import { yupResolver } from '@hookform/resolvers/yup'
import classNames from 'classnames'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { OffererMemberStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Layout } from 'app/App/layout/Layout'
import { GET_MEMBERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { OffererLinkEvents } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullDownIcon from 'icons/full-down.svg'
import fullUpIcon from 'icons/full-up.svg'
import { validationSchema } from 'pages/Collaborators/validationSchema'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './Collaborators.module.scss'

const SUCCESS_MESSAGE = "L'invitation a bien été envoyée."
const ERROR_MESSAGE = 'Une erreur est survenue lors de l’envoi de l’invitation.'

type UserEmailFormValues = {
  email: string
}

export const Collaborators = (): JSX.Element | null => {
  const offererId = useSelector(selectCurrentOffererId)

  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const [displayAllMembers, setDisplayAllMembers] = useState(false)

  const [showInvitationForm, setShowInvitationForm] = useState(false)

  const { data } = useSWR(
    [GET_MEMBERS_QUERY_KEY, offererId],
    ([, offererIdParam]) =>
      !offererIdParam ? null : api.getOffererMembers(offererIdParam),
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
      notify.success(SUCCESS_MESSAGE)
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400 && error.body.email) {
        setError('email', { message: error.body.email })
      } else {
        notify.error(ERROR_MESSAGE)
      }
    }
  }

  const MAX_COLLABORATORS = 10

  if (!offererId) {
    return null
  }

  return (
    <Layout mainHeading="Collaborateurs">
      <section className={styles['section']}>
        <h2 className={styles['main-list-title']}>Liste des collaborateurs</h2>

        {members.length > 0 && (
          <div className={styles['members-container']}>
            <div className={styles['members-inner']}>
              <table className={styles['members-list']}>
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
                            {status === OffererMemberStatus.VALIDATED
                              ? 'Validé'
                              : 'En attente'}
                          </td>
                        </tr>
                      )
                  )}
                </tbody>
              </table>
            </div>
            {members.length > MAX_COLLABORATORS && (
              <Button
                onClick={() => setDisplayAllMembers(!displayAllMembers)}
                variant={ButtonVariant.TERNARY}
                icon={displayAllMembers ? fullUpIcon : fullDownIcon}
                className={styles['display-all-members-button']}
              >
                {displayAllMembers
                  ? 'Voir moins de collaborateurs'
                  : 'Voir plus de collaborateurs'}
              </Button>
            )}
          </div>
        )}

        {!showInvitationForm ? (
          <Button
            variant={ButtonVariant.SECONDARY}
            onClick={() => {
              logEvent(OffererLinkEvents.CLICKED_ADD_COLLABORATOR, {
                offererId: offererId,
              })
              setShowInvitationForm(true)
            }}
          >
            Ajouter un collaborateur
          </Button>
        ) : (
          <>
            <h3 className={styles['subtitle']}>Ajout de collaborateurs</h3>
            <p className={styles['description']}>
              Vous pouvez inviter des collaborateurs à rejoindre votre espace.
              Une invitation leur sera envoyée par email. Vous serez notifié
              quand ils auront rejoint l’espace.
            </p>
            <form
              className={styles['invitation-form']}
              onSubmit={handleSubmit(onSubmit)}
            >
              <FormLayout>
                <FormLayout.Row className={styles['invitation-email-wrapper']}>
                  <TextInput
                    className={styles['invitation-email-field']}
                    label="Adresse email"
                    description="Format : email@exemple.com"
                    error={errors.email?.message}
                    required={true}
                    asterisk={false}
                    {...register('email')}
                  />
                  <Button
                    type="submit"
                    isLoading={isSubmitting}
                    className={styles['add-member-button']}
                    data-error={errors.email?.message ? 'true' : 'false'}
                  >
                    Inviter
                  </Button>
                </FormLayout.Row>
              </FormLayout>
            </form>
          </>
        )}
      </section>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Collaborators
