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
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  ensureCurrentUser,
  ensureSelectedPartnerVenue,
} from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import { SynchronizedBanner } from '@/pages/IndividualOffer/components/SynchronizedBanner/SynchronizedBanner'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import type { IndividualOfferPracticalInfosFormValues } from '../../commons/types'
import { CGU_LINK } from './constants'
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
}: Readonly<IndividualOfferPracticalInfosFormProps>) {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed

  const form = useFormContext<IndividualOfferPracticalInfosFormValues>()

  const currentUser = useAppSelector(ensureCurrentUser)

  const receiveNotificationEmails = form.watch('receiveNotificationEmails')
  const bookingEmail = form.watch('bookingEmail')

  const isOfferDisabledOrSynchronized =
    isOfferDisabled(offer) || isOfferSynchronized(offer) || isVenueClosed

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
    <>
      {isOfferSynchronized(offer) && (
        <SynchronizedBanner providerName={offer?.lastProvider?.name} />
      )}
      <FormLayout fullWidthActions>
        <FormLayout.Section title="Informations pratiques">
          {subCategory?.canBeWithdrawable ? (
            <IndividualOfferPracticalInfosFormWithdrawal
              isFormDisabled={isOfferDisabledOrSynchronized}
            />
          ) : null}
          {!offer?.isEvent && (
            <FormLayout.Row mdSpaceAfter>
              <Banner
                title="Validation obligatoire"
                variant={BannerVariants.WARNING}
                description={`Sans validation de la contremarque, la réservation sera annulée et remise en vente après ${reimbursmentDelay} jours. ${offerWillBeReimbursed ? 'Vous ne serez pas remboursé.' : ''}`}
              ></Banner>
            </FormLayout.Row>
          )}
          <FormLayout.Row mdSpaceAfter>
            <TextArea
              {...form.register('withdrawalDetails')}
              label="Informations complémentaires"
              maxLength={500}
              disabled={isOfferDisabled(offer) || isVenueClosed}
              description="Ces informations seront communiquées aux jeunes après leur réservation."
            />
          </FormLayout.Row>
        </FormLayout.Section>
        {isPhysicalAndOffline && (
          <FormLayout.Section>
            <FormLayout.Row mdSpaceAfter>
              <Banner
                title="Livraison interdite"
                variant={BannerVariants.WARNING}
                actions={[
                  {
                    label: 'Consulter les conditions Générales d’Utilisation',
                    href: CGU_LINK,
                    isExternal: true,
                    icon: fullLinkIcon,
                    iconAlt: 'Nouvelle fenêtre',
                    type: 'link',
                  },
                ]}
                description="La livraison d’articles n’est pas autorisée. Consultez nos CGU pour plus d'informations."
              />
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
              disabled={isOfferDisabled(offer) || isVenueClosed}
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
              disabled={isOfferDisabledOrSynchronized}
              onChange={(e) => {
                if (e.target.checked && !bookingEmail) {
                  form.setValue(
                    'bookingEmail',
                    offer?.venue.bookingEmail ?? currentUser.email,
                    { shouldDirty: true }
                  )
                }

                form.setValue('receiveNotificationEmails', e.target.checked, {
                  shouldDirty: true,
                })
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
                disabled={isOfferDisabledOrSynchronized}
                description="Format : email@exemple.com"
                required
                requiredIndicator="explicit"
                error={form.formState.errors.bookingEmail?.message}
              />
            </FormLayout.Row>
          )}
        </FormLayout.Section>
      </FormLayout>
    </>
  )
}
