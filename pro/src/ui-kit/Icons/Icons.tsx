/* istanbul ignore file */
import React from 'react'

import { ReactComponent as AudioDisabilityIcon } from 'icons/audio-disability.svg'
import { ReactComponent as BuildingIcon } from 'icons/building.svg'
import { ReactComponent as CheckboxCheckIcon } from 'icons/checkbox-check.svg'
import { ReactComponent as CloseDialogIcon } from 'icons/close-dialog.svg'
import { ReactComponent as DropdownDisclosureDownBDisabledIcon } from 'icons/dropdown-disclosure-down-b-disabled.svg'
import { ReactComponent as DropdownDisclosureDownBIcon } from 'icons/dropdown-disclosure-down-b.svg'
import { ReactComponent as DropdownDisclosureDownSWIcon } from 'icons/dropdown-disclosure-down-s-w.svg'
import { ReactComponent as IcoAlertGrey } from 'icons/ico-alert-grey.svg'
import { ReactComponent as IcoAttention } from 'icons/ico-attention.svg'
import { ReactComponent as IcoBreadcrumbArrowRight } from 'icons/ico-breadcrumb-arrow-right.svg'
import { ReactComponent as IcoBulb } from 'icons/ico-bulb.svg'
import { ReactComponent as IcoCalendarDisabled } from 'icons/ico-calendar-disabled.svg'
import { ReactComponent as IcoCalendarV2 } from 'icons/ico-calendar-v2.svg'
import { ReactComponent as IcoCalendar } from 'icons/ico-calendar.svg'
import { ReactComponent as IcoCaretDown } from 'icons/ico-caret-down.svg'
import { ReactComponent as IcoCaretRight } from 'icons/ico-caret-right.svg'
import { ReactComponent as IcoClear } from 'icons/ico-clear.svg'
import { ReactComponent as IconDesk } from 'icons/ico-desk.svg'
import { ReactComponent as IcoDownloadFilled } from 'icons/ico-download-filled.svg'
import { ReactComponent as IcoDownload } from 'icons/ico-download.svg'
import { ReactComponent as IcoDuo } from 'icons/ico-duo.svg'
import { ReactComponent as IcoEuroGrey } from 'icons/ico-euro-grey.svg'
import { ReactComponent as IcoEuroV2 } from 'icons/ico-euro-v2.svg'
import { ReactComponent as IcoEuro } from 'icons/ico-euro.svg'
import { ReactComponent as IcoExternalSiteFilled } from 'icons/ico-external-site-filled.svg'
import { ReactComponent as IcoExternalSiteRedFilled } from 'icons/ico-external-site-red-filled.svg'
import { ReactComponent as IcoEyeClose } from 'icons/ico-eye-close.svg'
import { ReactComponent as IcoEyeHidden } from 'icons/ico-eye-hidden.svg'
import { ReactComponent as IcoEyeOpen } from 'icons/ico-eye-open.svg'
import { ReactComponent as GuichetFullIcon } from 'icons/ico-guichet-full.svg'
import { ReactComponent as HomeIcon } from 'icons/ico-home.svg'
import { ReactComponent as ListOffersIcon } from 'icons/ico-list-offers.svg'
import { ReactComponent as IcoMail } from 'icons/ico-mail.svg'
import { ReactComponent as IcoMiniArrowLeft } from 'icons/ico-mini-arrow-left.svg'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { ReactComponent as IcoMoreCircle } from 'icons/ico-more-circle.svg'
import { ReactComponent as IcoMoreHoriz } from 'icons/ico-more-horiz.svg'
import { ReactComponent as IcoNext } from 'icons/ico-next-S.svg'
import { ReactComponent as OffersIcon } from 'icons/ico-offers.svg'
import { ReactComponent as IcoOuterPen } from 'icons/ico-outer-pen.svg'
import { ReactComponent as IcoPassculture } from 'icons/ico-passculture.svg'
import { ReactComponent as IcoPenBlack } from 'icons/ico-pen-black.svg'
import { ReactComponent as IcoPen } from 'icons/ico-pen.svg'
import { ReactComponent as PlusCircleIcon } from 'icons/ico-plus-circle.svg'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import { ReactComponent as IcoRightCircleArrow } from 'icons/ico-right-circle-arrow.svg'
import { ReactComponent as IcoSearchGray } from 'icons/ico-search-gray.svg'
import { ReactComponent as SignoutIcon } from 'icons/ico-signout.svg'
import { ReactComponent as StatsIcon } from 'icons/ico-stats.svg'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'
import { ReactComponent as IcoStructure } from 'icons/ico-structure.svg'
import { ReactComponent as IcoTag } from 'icons/ico-tag.svg'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { ReactComponent as IcoTrash } from 'icons/ico-trash.svg'
import { ReactComponent as TropheeIcon } from 'icons/ico-trophee.svg'
import { ReactComponent as IcoUnavailableGradient } from 'icons/ico-unavailable-gradient.svg'
import { ReactComponent as IcoUnavailablePage } from 'icons/ico-unavailable-page.svg'
import { ReactComponent as IcoValideCercle } from 'icons/ico-valide-cercle.svg'
import { ReactComponent as IcoVenue } from 'icons/ico-venue.svg'
import { ReactComponent as WarningStocksIcon } from 'icons/ico-warning-stocks.svg'
import { ReactComponent as IcoClose } from 'icons/icons-close.svg'
import { ReactComponent as InfoPhoneIcon } from 'icons/info-phone.svg'
import { ReactComponent as InfoIcon } from 'icons/info.svg'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as LinearGradientIcon } from 'icons/linear-gradient.svg'
import { ReactComponent as LocationIcon } from 'icons/location.svg'
import { ReactComponent as MentalDisabilityIcon } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilityIcon } from 'icons/motor-disability.svg'
import { ReactComponent as OfferCardEuroIcon } from 'icons/offer-card-euro.svg'
import { ReactComponent as OpenDropdownIcon } from 'icons/open-dropdown.svg'
import { ReactComponent as PendingIcon } from 'icons/pending.svg'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import { ReactComponent as TickIcon } from 'icons/tick.svg'
import { ReactComponent as TicketCrossIcon } from 'icons/ticket-cross.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import { ReactComponent as ValidateIcon } from 'icons/validate.svg'
import { ReactComponent as VisualDisabilityIcon } from 'icons/visual-disability.svg'

import styles from './Icons.module.scss'

export const Icons = () => (
  <table className={styles.table}>
    <body>
      <tr>
        <td>
          <BuildingIcon />
        </td>
        <td>building</td>
      </tr>
      <tr>
        <td>
          <IcoVenue />
        </td>
        <td>ico-venue</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <CheckboxCheckIcon />
        </td>
        <td>checkbox-check</td>
      </tr>
      <tr>
        <td>
          <CloseDialogIcon />
        </td>
        <td>close-dialog</td>
      </tr>
      <tr>
        <td>
          <DropdownDisclosureDownBDisabledIcon />
        </td>
        <td>dropdown-disclosure-down-b-disabled</td>
      </tr>
      <tr>
        <td>
          <DropdownDisclosureDownBIcon />
        </td>
        <td>dropdown-disclosure-down-b</td>
      </tr>
      <tr>
        <td>
          <DropdownDisclosureDownSWIcon />
        </td>
        <td>dropdown-disclosure-down-s-w</td>
      </tr>
      <tr>
        <td>
          <IcoNext />
        </td>
        <td>ico-next</td>
      </tr>
      <tr>
        <td>
          <IcoAlertGrey />
        </td>
        <td>ico-alert-grey</td>
      </tr>
      <tr>
        <td>
          <IcoAttention />
        </td>
        <td>ico-attention</td>
      </tr>
      <tr>
        <td>
          <IcoBreadcrumbArrowRight />
        </td>
        <td>ico-breadcrumb-arrow-right</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <IcoMiniArrowRight />
        </td>
        <td>ico-mini-arrow-right-icon</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <IcoMiniArrowLeft />
        </td>
        <td>ico-mini-arrow-left-icon</td>
      </tr>
      <tr>
        <td>
          <IcoBulb />
        </td>
        <td>ico-bulb</td>
      </tr>
      <tr>
        <td>
          <IcoCalendarDisabled />
        </td>
        <td>ico-calendar-disabled</td>
      </tr>
      <tr>
        <td>
          <IcoCalendar />
        </td>
        <td>ico-calendar</td>
      </tr>
      <tr>
        <td>
          <IcoCalendarV2 />
        </td>
        <td>ico-calendar-v2</td>
      </tr>
      <tr>
        <td>
          <IcoCaretDown />
        </td>
        <td>ico-caret-down</td>
      </tr>
      <tr>
        <td>
          <IcoCaretRight />
        </td>
        <td>ico-caret-right</td>
      </tr>
      <tr>
        <td>
          <IcoClear />
        </td>
        <td>ico-clear</td>
      </tr>
      <tr>
        <td>
          <IcoDownloadFilled />
        </td>
        <td>ico-download-filled</td>
      </tr>
      <tr>
        <td>
          <IcoDownload />
        </td>
        <td>ico-download</td>
      </tr>
      <tr>
        <td>
          <IcoDuo />
        </td>
        <td>ico-duo</td>
      </tr>
      <tr>
        <td>
          <IcoEuroGrey />
        </td>
        <td>ico-euro-grey</td>
      </tr>
      <tr>
        <td>
          <IcoEuro />
        </td>
        <td>ico-euro</td>
      </tr>
      <tr>
        <td>
          <IcoEuroV2 />
        </td>
        <td>ico-euro-v2</td>
      </tr>
      <tr>
        <td>
          <IcoExternalSiteFilled />
        </td>
        <td>ico-external-site-filled</td>
      </tr>
      <tr>
        <td>
          <IcoExternalSiteRedFilled />
        </td>
        <td>ico-external-site-red-filled</td>
      </tr>
      <tr>
        <td>
          <IcoEyeClose />
        </td>
        <td>ico-eye-close</td>
      </tr>
      <tr>
        <td>
          <IcoEyeHidden />
        </td>
        <td>ico-eye-hidden</td>
      </tr>
      <tr>
        <td>
          <IcoEyeOpen />
        </td>
        <td>ico-eye-open</td>
      </tr>
      <tr>
        <td>
          <IcoMail />
        </td>
        <td>ico-mail</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <IcoMoreCircle />
        </td>
        <td>ico-more-circle</td>
      </tr>
      <tr>
        <td>
          <IcoMoreHoriz />
        </td>
        <td>ico-more-horiz</td>
      </tr>
      <tr>
        <td>
          <IcoOuterPen />
        </td>
        <td>ico-outer-pen</td>
      </tr>
      <tr>
        <td>
          <IcoPassculture />
        </td>
        <td>ico-passculture</td>
      </tr>
      <tr>
        <td>
          <IcoPenBlack />
        </td>
        <td>ico-pen-black</td>
      </tr>
      <tr>
        <td>
          <IcoPen />
        </td>
        <td>ico-pen</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <IcoPlus />
        </td>
        <td>ico-plus</td>
      </tr>
      <tr>
        <td>
          <PlusCircleIcon />
        </td>
        <td>ico-plus-circle</td>
      </tr>
      <tr>
        <td>
          <IcoRightCircleArrow />
        </td>
        <td>ico-right-circle-arrow</td>
      </tr>
      <tr>
        <td>
          <IcoSearchGray />
        </td>
        <td>ico-search-gray</td>
      </tr>
      <tr>
        <td>
          <IcoStructure />
        </td>
        <td>ico-structure</td>
      </tr>
      <tr>
        <td>
          <IcoTag />
        </td>
        <td>ico-tag</td>
      </tr>
      <tr>
        <td>
          <IcoTrash />
        </td>
        <td>ico-trash</td>
      </tr>
      <tr>
        <td>
          <TrashFilledIcon />
        </td>
        <td>ico-trash-filled</td>
      </tr>
      <tr>
        <td>
          <IcoUnavailableGradient />
        </td>
        <td>ico-unavailable-gradient</td>
      </tr>
      <tr>
        <td>
          <IcoUnavailablePage />
        </td>
        <td>ico-unavailable-page</td>
      </tr>
      <tr>
        <td>
          <IcoValideCercle />
        </td>
        <td>ico-valide-cercle</td>
      </tr>
      <tr>
        <td>
          <IcoClose />
        </td>
        <td>icons-close</td>
      </tr>
      <tr>
        <td>
          <InfoPhoneIcon />
        </td>
        <td>info-phone</td>
      </tr>
      <tr>
        <td>
          <InfoIcon />
        </td>
        <td>info</td>
      </tr>
      <tr>
        <td>
          <LibraryIcon />
        </td>
        <td>library</td>
      </tr>
      <tr>
        <td>
          <LinearGradientIcon />
        </td>
        <td>linear-gradient</td>
      </tr>
      <tr>
        <td>
          <LocationIcon />
        </td>
        <td>location</td>
      </tr>
      <tr>
        <td>
          <AudioDisabilityIcon />
        </td>
        <td>audio-disability</td>
      </tr>
      <tr>
        <td>
          <VisualDisabilityIcon />
        </td>
        <td>visual-disability</td>
      </tr>
      <tr>
        <td>
          <MentalDisabilityIcon />
        </td>
        <td>mental-disability</td>
      </tr>
      <tr>
        <td>
          <MotorDisabilityIcon />
        </td>
        <td>motor-disability</td>
      </tr>
      <tr>
        <td>
          <OfferCardEuroIcon />
        </td>
        <td>offer-card-euro</td>
      </tr>
      <tr>
        <td>
          <OpenDropdownIcon />
        </td>
        <td>open-dropdown</td>
      </tr>
      <tr>
        <td>
          <ResetIcon />
        </td>
        <td>reset</td>
      </tr>
      <tr>
        <td>
          <TickIcon />
        </td>
        <td>tick</td>
      </tr>
      <tr>
        <td>
          <TicketCrossIcon />
        </td>
        <td>ticket-cross</td>
      </tr>
      <tr>
        <td>
          <UserIcon />
        </td>
        <td>user</td>
      </tr>

      <tr>
        <td>
          <TropheeIcon />
        </td>
        <td>ico-trophee</td>
      </tr>
      <tr>
        <td>
          <HomeIcon />
        </td>
        <td>ico-home</td>
      </tr>
      <tr>
        <td>
          <IconDesk />
        </td>
        <td>ico-desk</td>
      </tr>
      <tr>
        <td>
          <SignoutIcon />
        </td>
        <td>ico-signout</td>
      </tr>
      <tr>
        <td>
          <OffersIcon />
        </td>
        <td>ico-offers</td>
      </tr>
      <tr>
        <td>
          <ListOffersIcon />
        </td>
        <td>ico-list-offers</td>
      </tr>
      <tr>
        <td>
          <StatsIcon />
        </td>
        <td>ico-stats</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <StatusInactiveIcon />
        </td>
        <td>ico-status-inactive</td>
      </tr>
      <tr>
        <td className={styles['with-background']}>
          <StatusValidatedIcon />
        </td>
        <td>ico-status-validated</td>
      </tr>
      <tr>
        <td>
          <WarningStocksIcon />
        </td>
        <td>ico-warning-stocks</td>
      </tr>
      <tr>
        <td>
          <GuichetFullIcon />
        </td>
        <td>ico-guichet-full</td>
      </tr>
      <tr>
        <td>
          <PendingIcon />
        </td>
        <td>pending</td>
      </tr>
      <tr>
        <td>
          <ValidateIcon />
        </td>
        <td>validate</td>
      </tr>
    </body>
  </table>
)
