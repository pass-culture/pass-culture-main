import { useFormContext } from 'react-hook-form'

import {
  type GetIndividualOfferWithAddressResponseModel,
  type GetOfferStockResponseModel,
  SubcategoryIdEnum,
  type SubcategoryResponseModel,
} from '@/apiClient/v1'
import { REIMBURSEMENT_RULES } from '@/commons/core/Finances/constants'
import { CATEGORY_STATUS } from '@/commons/core/Offers/constants'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import type { IndividualOfferPracticalInfosFormValues } from '../../commons/types'
import styles from './IndividualOfferPracticalInfosForm.module.scss'
import { IndividualOfferPracticalInfosFormWithdrawal } from './IndividualOfferPracticalInfosFormWithdrawal/IndividualOfferPracticalInfosFormWithdrawal'

export type IndividualOfferPracticalInfosFormProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  subCategory?: SubcategoryResponseModel
  stocks: GetOfferStockResponseModel[]
}

export function IndividualOfferPracticalInfosForm({
  offer,
  subCategory,
  stocks,
}: IndividualOfferPracticalInfosFormProps) {
  const form = useFormContext<IndividualOfferPracticalInfosFormValues>()

  const {
    currentUser: { email },
  } = useCurrentUser()

  const receiveNotificationEmails = form.watch('receiveNotificationEmails')
  const bookingEmail = form.watch('bookingEmail')

  const isFormDisabled = isOfferDisabled(offer)

  const hasNonFreeStock = stocks.some((s) => Boolean(s.price))

  const offerWillBeReimbursed =
    (subCategory?.reimbursementRule === REIMBURSEMENT_RULES.STANDARD ||
      subCategory?.reimbursementRule === REIMBURSEMENT_RULES.BOOK) &&
    hasNonFreeStock

  const reimbursmentDelay =
    subCategory?.id === SubcategoryIdEnum.LIVRE_PAPIER ? 10 : 30

  const isPhysicalAndOffline =
    !subCategory?.isEvent &&
    subCategory?.onlineOfflinePlatform === CATEGORY_STATUS.OFFLINE

  return (
    <FormLayout fullWidthActions>
      <FormLayout.Section title="Informations pratiques">
        {subCategory?.canBeWithdrawable ? (
          <IndividualOfferPracticalInfosFormWithdrawal
            isFormDisabled={isFormDisabled}
          />
        ) : null}
        {!offer?.isEvent && (
          <FormLayout.Row mdSpaceAfter>
            <Callout variant={CalloutVariant.WARNING}>
              La validation de la contremarque est obligatoire
              {offerWillBeReimbursed
                ? ' pour que votre structure soit remboursée'
                : ''}
              , sinon la réservation sera automatiquement annulée et remise en
              vente au bout de {reimbursmentDelay} jours.
            </Callout>
          </FormLayout.Row>
        )}
        <FormLayout.Row mdSpaceAfter>
          <TextArea
            {...form.register('withdrawalDetails')}
            label="Informations complémentaires"
            maxLength={500}
            disabled={isFormDisabled}
            description="Ces informations seront communiquées aux jeunes après leur réservation."
          />
        </FormLayout.Row>
      </FormLayout.Section>
      {isPhysicalAndOffline && (
        <FormLayout.Section>
          <FormLayout.Row mdSpaceAfter>
            <Callout
              variant={CalloutVariant.WARNING}
              links={[
                {
                  label: 'Consulter les conditions Générales d’Utilisation',
                  href: 'https://pass.culture.fr/cgu-professionnels',
                  isExternal: true,
                },
              ]}
            >
              La livraison d’article est interdite. Pour plus d’informations,
              veuillez consulter nos CGU.
            </Callout>
          </FormLayout.Row>
        </FormLayout.Section>
      )}
      <FormLayout.Section
        title="Lien de réservation externe en l’absence de crédit"
        description="S’ils ne disposent pas ou plus de crédit, les utilisateurs de
          l’application seront redirigés sur ce lien pour pouvoir néanmoins
          profiter de votre offre."
      >
        <FormLayout.Row mdSpaceAfter>
          <TextInput
            {...form.register('externalTicketOfficeUrl')}
            label="URL de votre site ou billetterie"
            type="url"
            disabled={isFormDisabled}
            description="Format : https://exemple.com"
            error={form.formState.errors.externalTicketOfficeUrl?.message}
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <FormLayout.Section title="Notifications">
        <FormLayout.Row mdSpaceAfter>
          <Checkbox
            label="Être notifié par email des réservations"
            checked={Boolean(receiveNotificationEmails)}
            disabled={isFormDisabled}
            onChange={(e) => {
              if (e.target.checked && !bookingEmail) {
                form.setValue(
                  'bookingEmail',
                  offer?.venue.bookingEmail ?? email
                )
              }

              form.setValue('receiveNotificationEmails', e.target.checked)
            }}
          />
        </FormLayout.Row>
        {receiveNotificationEmails && (
          <FormLayout.Row className={styles['email-row']} mdSpaceAfter>
            <TextInput
              {...form.register('bookingEmail')}
              type="email"
              label="Email auquel envoyer les notifications"
              maxCharactersCount={90}
              disabled={isFormDisabled}
              description="Format : email@exemple.com"
              required
              error={form.formState.errors.bookingEmail?.message}
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </FormLayout>
  )
}
