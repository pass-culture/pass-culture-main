/* istanbul ignore file */
import cn from 'classnames'
import React, { useState } from 'react'

import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import BaseInput from 'ui-kit/form/shared/BaseInput'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Title } from 'ui-kit/typography'

import styles from './Icons.module.scss'

const fuzzyMatch = (pattern: string, str: string) => {
  pattern = '.*' + pattern.toLowerCase().split('').join('.*') + '.*'
  const re = new RegExp(pattern)
  return re.test(str.toLowerCase())
}

interface IconListItem {
  src: string
  viewBox?: string
}

const iconList = [
  // Cleaned !
  // Those icons are put in the order of the design library here:
  // https://www.figma.com/file/AEXCkb4KbUyPmB4BRFa88s/PRO---Library?type=design&node-id=8059-111986&t=sLfFXFbaXGFLjdhX-0

  // Full icons
  { src: 'icons/full-pause.svg' },
  { src: 'icons/full-play.svg' },
  { src: 'icons/full-mail.svg' }, // TODO 2 uses left inside ButtonLink, 1 use left inside SubmitButton
  { src: 'icons/full-edit.svg' }, // TODO 7 uses left in <ButtonLink>s
  { src: 'icons/full-duplicate.svg' }, // TODO still used in 1 Button
  { src: 'icons/full-back.svg' },
  { src: 'icons/full-download.svg' }, // TODO 3 uses left inside <Button> and <ButtonLink>
  { src: 'icons/full-parameters.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/full-more-bis.svg' }, // TODO still in 2 ButtonLink and 1 Button
  { src: 'icons/full-down.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/full-up.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/full-right.svg' },
  { src: 'icons/full-arrow-right.svg' },

  // Stroke icons
  { src: 'icons/stroke-user.svg' }, // TODO 4 uses left inside <Tabs>
  { src: 'icons/stroke-error.svg' },
  { src: 'icons/stroke-thing.svg' },
  { src: 'icons/stroke-info-phone.svg' },
  { src: 'icons/stroke-building.svg' },
  { src: 'icons/stroke-code.svg' },
  { src: 'icons/stroke-accessibility-ear.svg' },

  // Shadow icons
  { src: 'icons/shadow-tips-help.svg', viewBox: '0 0 22 26' },

  // Not cleaned
  { src: 'icons/ico-calendar-big.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-calendar-disabled.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-calendar-v2.svg', viewBox: '0 0 24 25' },
  { src: 'icons/ico-caret-down.svg', viewBox: '0 0 13 10' },
  { src: 'icons/ico-caret-right.svg', viewBox: '0 0 10 13' },
  { src: 'icons/checkbox-check.svg', viewBox: '0 0 10 8' },
  { src: 'icons/checkbox.svg', viewBox: '0 0 10 8' },
  { src: 'icons/ico-clear-red.svg', viewBox: '0 0 15 14' },
  { src: 'icons/ico-close-b.svg', viewBox: '0 0 17 16' },
  { src: 'icons/close-dialog.svg', viewBox: '0 0 24 24' },
  { src: 'icons/icons-close.svg', viewBox: '0 0 18 18' },
  { src: 'icons/ico-close-r.svg', viewBox: '0 0 17 16' },
  { src: 'icons/close-tag.svg', viewBox: '0 0 10 10' },
  { src: 'icons/ico-compta.svg', viewBox: '0 0 20 23' },
  { src: 'icons/ico-desk.svg', viewBox: '0 0 49 48' },
  { src: 'icons/ico-double-check.svg' },
  {
    src: 'icons/dropdown-disclosure-down-b-disabled.svg',
    viewBox: '0 0 14 7',
  },
  { src: 'icons/dropdown-disclosure-down-b.svg', viewBox: '0 0 14 7' },
  { src: 'icons/dropdown-disclosure-down-s-w.svg', viewBox: '0 0 14 7' },
  { src: 'icons/ico-duo.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-duplicate-offer.svg', viewBox: '0 0 40 40' },
  { src: 'icons/ico-email-red.svg', viewBox: '0 0 25 24' },
  { src: 'icons/error.svg', viewBox: '0 0 18 18' },
  { src: 'icons/ico-euro-grey.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-euro-v2.svg', viewBox: '0 0 24 25' },
  { src: 'icons/ico-external-site-filled.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-fill-external-link.svg', viewBox: '0 0 25 24' },
  { src: 'icons/ico-external-site-red.svg', viewBox: '0 0 25 24' },
  { src: 'icons/external-site.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-eye-full-close.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-eye-full-open.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-eye-hidden.svg', viewBox: '0 0 88 88' },
  { src: 'icons/ico-eye-open-filled-black.svg' },
  { src: 'icons/ico-filter-status-active.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-filter-status-black.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-filter-status-red.svg', viewBox: '0 0 24 24' },
  { src: 'icons/fraud.svg', viewBox: '0 0 88 88' },
  { src: 'icons/ico-geoloc-solid.svg', viewBox: '0 0 21 30' },
  { src: 'icons/ico-guichet-full.svg' },
  { src: 'icons/ico-home.svg' },
  { src: 'icons/ico-hourglass.svg' },
  { src: 'icons/info.svg', viewBox: '0 0 78 78' },
  { src: 'icons/ico-is-valid.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-left-arrow.svg', viewBox: '0 0 24 24' },
  { src: 'icons/library.svg', viewBox: '0 0 49 48' },
  { src: 'icons/linear-gradient.svg', viewBox: '0 0 623 1024' }, // TODO replace by a jpg/png
  { src: 'icons/loader.svg', viewBox: '0 0 32 32' },
  { src: 'icons/loader-pc.svg', viewBox: '0 0 56 56' },
  { src: 'icons/location.svg', viewBox: '0 0 24 24' },
  { src: 'icons/logo-allocine.svg', viewBox: '0 0 100 24' }, // TODO replace by a jpg/png
  { src: 'icons/logo-boost.svg', viewBox: '0 0 386 254' }, // TODO replace by a jpg/png
  { src: 'icons/logo-cgr.svg', viewBox: '0 0 283.46 255.12' }, // TODO replace by a jpg/png
  { src: 'icons/logo-cdi-bookshop.svg', viewBox: '0 0 804 167.35' },
  { src: 'icons/logo-cine-digital-service.svg', viewBox: '0 0 529 169' },
  { src: 'icons/logo-decitre.svg', viewBox: '0 0 483 320' },
  { src: 'icons/logo-fnac.svg', viewBox: '0 0 29 24' },
  { src: 'icons/logo-libraires.svg', viewBox: '0 0 74 24' },
  { src: 'icons/logo-librisoft.svg', viewBox: '0 0 526 206' },
  { src: 'icons/logo-openAgenda.svg', viewBox: '0 0 60 90' },
  { src: 'icons/logo-pass-culture.svg', viewBox: '0 0 114 84' },
  { src: 'icons/logo-pass-culture-header.svg', viewBox: '0 0 119 40' },
  { src: 'icons/logo-pass-culture-white.svg', viewBox: '0 0 282 120' },
  { src: 'icons/logo-praxiel.svg', viewBox: '0 0 29 24' },
  { src: 'icons/logo-tmic-ellipses.svg', viewBox: '0 0 390 120' },
  { src: 'icons/logo-titeLive.svg', viewBox: '0 0 75 24' },
  { src: 'icons/mental-disability.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-mini-arrow-left.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-mini-arrow-right.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-more-circle.svg', viewBox: '0 0 25 24' },
  { src: 'icons/ico-more-horiz.svg', viewBox: '0 0 24 24' },
  { src: 'icons/motor-disability.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-new-offer.svg', viewBox: '0 0 40 40' },
  { src: 'icons/ico-next-S.svg', viewBox: '0 0 11 23' },
  { src: 'icons/ico-no-bookings.svg', viewBox: '0 0 124 124' },
  { src: 'icons/ico-404.svg', viewBox: '0 0 308 194' },
  { src: 'icons/ico-notification-error-red.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-notification-success.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-placeholder-offer-image.svg', viewBox: '0 0 80 80' },
  { src: 'icons/ico-offers.svg', viewBox: '0 0 48 49' },
  { src: 'icons/open-dropdown.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-other-download.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-other.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-outer-pen.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-pen-black-big.svg' },
  { src: 'icons/ico-pen-black.svg', viewBox: '0 0 20 20' },
  { src: 'icons/pending.svg', viewBox: '0 0 44 44' },
  { src: 'icons/ico-phone.svg', viewBox: '0 0 16 16' },
  { src: 'icons/picto-info-grey.svg', viewBox: '0 0 22 22' },
  { src: 'icons/picto-info.svg', viewBox: '0 0 22 22' },
  { src: 'icons/picto-tip.svg', viewBox: '0 0 18 18' },
  { src: 'icons/ico-radio-off.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-radio-on.svg', viewBox: '0 0 16 16' },
  { src: 'icons/reset.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-right-arrow.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-screen-play.svg', viewBox: '0 0 33 32' },
  { src: 'icons/ico-search-gray.svg', viewBox: '0 0 124 125' },
  { src: 'icons/ico-separator.svg', viewBox: '0 0 20 1' },
  { src: 'icons/ico-signout.svg', viewBox: '0 0 48 49' },
  { src: 'icons/ico-star.svg', viewBox: '0 0 38 36' },
  { src: 'icons/ico-stars.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-stats.svg' },
  { src: 'icons/ico-stats-grey.svg', viewBox: '0 0 88 88' },
  { src: 'icons/ico-status-booked.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-cancelled.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-double-validated.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-draft.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-expired.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-inactive.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-status-pending.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-pending-full.svg', viewBox: '0 0 21 20' },
  { src: 'icons/ico-status-pending-tag.svg', viewBox: '0 0 12 14' },
  { src: 'icons/ico-status-reimbursed.svg', viewBox: '0 0 22 14' },
  { src: 'icons/ico-status-rejected.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-sold-out.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-status-validated.svg', viewBox: '0 0 17 17' },
  { src: 'icons/ico-status-validated-white.svg', viewBox: '0 0 17 17' },
  { src: 'icons/ico-structure.svg', viewBox: '0 0 30 25' },
  { src: 'icons/ico-structure-r.svg', viewBox: '0 0 28 25' },
  { src: 'icons/ico-success.svg', viewBox: '0 0 88 88' },
  { src: 'icons/ico-tag.svg', viewBox: '0 0 33 33' },
  { src: 'icons/ico-template-offer.svg' },
  { src: 'icons/ticket-cross.svg', viewBox: '0 0 100 80' },
  { src: 'icons/ico-trash.svg' },
  { src: 'icons/ico-trophee.svg', viewBox: '0 0 24 25' },
  { src: 'icons/ico-unavailable-gradient.svg', viewBox: '0 0 178 100' },
  { src: 'icons/ico-unavailable-page.svg', viewBox: '0 0 317 198' },
  { src: 'icons/ico-unfold.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-unavailable-page-white.svg', viewBox: '0 0 317 198' },
  { src: 'icons/ico-user.svg', viewBox: '0 0 17 16' },
  { src: 'icons/ico-validate-green.svg', viewBox: '0 0 15 14' },
  { src: 'icons/validate.svg', viewBox: '0 0 56 56' },
  { src: 'icons/ico-validate-p.svg', viewBox: '0 0 17 17' },
  { src: 'icons/ico-validate-purple.svg', viewBox: '0 0 15 14' },
  { src: 'icons/ico-valide-cercle.svg', viewBox: '0 0 88 88' },
  { src: 'icons/visual-disability.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-warning-grey.svg' },
  { src: 'icons/ico-warning.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-subcategory.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-like.svg' },
  { src: 'icons/ico-liked.svg' },
  { src: 'icons/ico-chevron-adage.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-alert-grey.svg', viewBox: '0 0 80 80' },
  { src: 'icons/ico-circle-arrow.svg', viewBox: '0 0 20 20' },
  { src: 'icons/add-user.svg', viewbox: '0 0 106 74' },
  { src: 'icons/ico-alert-filled.svg', viewbox: '0 0 24 24' },
  { src: 'icons/ico-arrow-up-b.svg', viewbox: '0 0 24 24' },
  { src: 'icons/ico-calendar-check.svg', viewbox: '0 0 48 48' },
  { src: 'icons/icon-calendar.svg', viewbox: '0 0 30 30' },
  { src: 'icons/ico-case.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-clear.svg', viewbox: '4 4 40 40' },
  { src: 'icons/ico-clock.svg', viewbox: '0 0 24 24' },
  { src: 'icons-close.svg', viewbox: '0 0 18 18' },
  { src: 'icons/ico-date.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-disconnect-full.svg', viewbox: '0 0 40 40' },
  { src: 'icons/ico-euro.svg', viewbox: '0 0 24 24' },
  { src: 'icons/ico-events.svg', viewbox: '0 0 24 24' },
  { src: 'icons/ico-external-site.svg', viewbox: '0 0 20 20' },
  { src: 'icons/ico-external-site-red-filled.svg', viewbox: '0 0 20 20' },
  { src: 'icons/ico-eye-close.svg', viewbox: '0 0 20 20' },
  { src: 'icons/ico-eye-open.svg', viewbox: '0 0 20 20' },
  { src: 'icons/ico-help-S.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-info-wrong.svg', viewbox: '0 0 78 78' },
  { src: 'icons/ico-key.svg', viewbox: '0 0 20 20' },
  { src: 'icons/logo-pass-culture-dark.svg', viewbox: '0 0 71 24' },
  { src: 'icons/ico-mail-outline.svg', viewbox: '0 0 82 67' },
  { src: 'icons/ico-notification-error.svg', viewbox: '0 0 24 24' },
  { src: 'icons/offer-card-euro.svg', viewbox: '0 0 30 30' },
  { src: 'icons/other-offer.svg', viewbox: '0 0 30 30' },
  { src: 'icons/party.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-passculture.svg', viewbox: '0 0 30 30' },
  { src: 'icons/ico-plus-circle.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-search.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-ticket-plus-full.svg', viewbox: '0 0 20 20' },
  { src: 'icons/ico-trash-filled.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-user-circled-w.svg', viewbox: '0 0 40 40' },
  { src: 'icons/ico-valid.svg', viewbox: '0 0 24 24' },
  { src: 'icons/venue-2.svg', viewbox: '0 0 40 40' },
  { src: 'icons/ico-venue.svg', viewbox: '0 0 28 23' },
  { src: 'icons/ico-virtual-event.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-virtual-thing.svg', viewbox: '0 0 48 48' },
  { src: 'icons/ico-institution.svg', viewbox: '0 0 18 18' },
  { src: 'icons/logo-pass-culture-adage.svg', viewbox: '0 0 120 39' },
]

export const Icons = () => {
  const [filteredIcons, setFilteredIcons] = useState<IconListItem[]>(iconList)
  const [whiteIcon, setWhiteIcon] = useState<boolean>(false)
  const [blackBackground, setBlackBackground] = useState<boolean>(false)

  const handleSearchOnChange: React.ChangeEventHandler<
    HTMLInputElement
  > = e => {
    e.stopPropagation()
    const search = e.target.value
    const newFilteredIcons = iconList.filter(iconListItem =>
      fuzzyMatch(search, iconListItem.src)
    )
    setFilteredIcons(newFilteredIcons)
  }

  const onClickToggleIconColor = () => {
    setWhiteIcon(current => !current)
  }
  const onClickToggleBackgroundColor = () => {
    setBlackBackground(current => !current)
  }
  const onClick: React.MouseEventHandler<HTMLDivElement> = e => {
    e.persist()
    const target = e.currentTarget as Element

    navigator.clipboard.writeText(target.getAttribute('data-src') ?? '')

    target.classList.add(styles['copy-to-clipboard'])
    const timeoutId = setTimeout(() => {
      target.classList.remove(styles['copy-to-clipboard'])
      clearTimeout(timeoutId)
    }, 600)
  }

  return (
    <div
      className={cn(styles['icon-stories'], {
        [styles['icon-white']]: whiteIcon,
        [styles['background-black']]: blackBackground,
      })}
    >
      <div className={styles['options']}>
        <p>
          Les couleurs des icons sont normalisé en noir (via la propriété css (
          <code> fill </code>)
        </p>
        <div className={styles['button-group']}>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={onClickToggleIconColor}
          >
            {whiteIcon
              ? 'Afficher les icônes en noir'
              : 'Afficher les icônes en blanc'}
          </Button>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={onClickToggleBackgroundColor}
          >
            {blackBackground
              ? 'Afficher les backgrounds en blanc'
              : 'Afficher les backgrounds en noir'}
          </Button>
        </div>
      </div>

      <Title level={1}>Liste des icones</Title>

      <div className={styles['search-input-container']}>
        <BaseInput
          className={styles['search-input']}
          name="search"
          onChange={handleSearchOnChange}
          placeholder="Rechercher ..."
        />
      </div>

      <div className={styles['icon-list']}>
        {filteredIcons.map(icon => {
          const fileNameParts = icon.src.split('/')
          const iconName = fileNameParts[fileNameParts.length - 1].split('.')[0]

          return (
            <div
              key={icon.src}
              className={styles['container']}
              onClick={onClick}
              data-src={icon.src}
            >
              <div className={styles['copy-to-clipboard-wrapper']}>
                <span className={styles['copy-to-clipboard-name']}>
                  Copié !
                </span>
              </div>
              <div className={styles['icon-container']}>
                <SvgIcon
                  src={icon.src}
                  alt={icon.src}
                  viewBox={icon.viewBox}
                  className={styles['icon']}
                />
              </div>
              <div className={styles['name-container']}>
                <span className={styles['name']}>{iconName}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
