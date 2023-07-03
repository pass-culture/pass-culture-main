/* istanbul ignore file */
import React, { useState } from 'react'

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

// Cleaned !
// Those icons are put in the order of the design library here:
// https://www.figma.com/file/AEXCkb4KbUyPmB4BRFa88s/PRO---Library?type=design&node-id=8059-111986&t=sLfFXFbaXGFLjdhX-0
const fullIcons: IconListItem[] = [
  { src: 'icons/full-pause.svg' },
  { src: 'icons/full-play.svg' },
  { src: 'icons/full-validate.svg' },
  { src: 'icons/full-clear.svg' },
  { src: 'icons/full-info.svg' },
  { src: 'icons/full-error.svg' },
  { src: 'icons/full-help.svg' },
  { src: 'icons/full-link.svg' }, // TODO 17 uses left inside <ButtonLink> and <Banner> and <InternalBanner>
  { src: 'icons/full-more.svg' }, // TODO still in 2 ButtonLink and 1 Button
  { src: 'icons/full-mail.svg' }, // TODO 2 uses left inside ButtonLink, 1 use left inside SubmitButton
  { src: 'icons/full-edit.svg' }, // TODO 7 uses left in <ButtonLink>s
  { src: 'icons/full-duplicate.svg' }, // TODO still used in 1 Button
  { src: 'icons/full-hide.svg' }, // TODO still used in 1 ConfirmDialog
  { src: 'icons/full-like.svg' },
  { src: 'icons/full-back.svg' },
  { src: 'icons/full-next.svg' }, // TODO still used
  { src: 'icons/full-wait.svg' },
  { src: 'icons/full-refresh.svg' }, // TODO still unsed in <Button>s
  { src: 'icons/full-download.svg' }, // TODO 3 uses left inside <Button> and <ButtonLink>
  { src: 'icons/full-parameters.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/full-key.svg' }, // TODO 1 use left inside a <ButtonLink>
  { src: 'icons/full-plus.svg' }, // TODO still in 2 ButtonLink and 1 Button
  { src: 'icons/full-sort.svg' },
  { src: 'icons/full-down.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/full-up.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/full-left.svg' }, // TODO 2 use left inside a <Button>
  { src: 'icons/full-right.svg' }, // TODO 2 use left inside a <Button>
  { src: 'icons/full-arrow-right.svg' },
  { src: 'icons/full-disclosure-close.svg' },
  { src: 'icons/full-disclosure-open.svg' },
]

const strokeIcons: IconListItem[] = [
  { src: 'icons/stroke-user.svg' }, // TODO 4 uses left inside <Tabs>
  { src: 'icons/stroke-error.svg' },
  { src: 'icons/stroke-warning.svg' },
  { src: 'icons/stroke-info.svg' },
  { src: 'icons/stroke-valid.svg' }, // TODO 1 use left inside <Banner>
  { src: 'icons/stroke-wrong.svg' },
  { src: 'icons/stroke-more.svg' }, // TODO 1 use left inside a <Button>
  { src: 'icons/stroke-euro.svg' }, // TODO 3 use left inside a <TextInput>
  { src: 'icons/stroke-events.svg' },
  { src: 'icons/stroke-thing.svg' },
  { src: 'icons/stroke-duo.svg' },
  { src: 'icons/stroke-virtual-event.svg' },
  { src: 'icons/stroke-virtual-thing.svg' },
  { src: 'icons/stroke-template-offer.svg' },
  { src: 'icons/stroke-mail.svg' }, // TODO 2 uses left in <Dialog>
  { src: 'icons/stroke-phone.svg' },
  { src: 'icons/stroke-home.svg' },
  { src: 'icons/stroke-building.svg' },
  { src: 'icons/stroke-desk.svg' },
  { src: 'icons/stroke-show.svg' }, // TODO 1 use left inside Button (PasswordInput)
  { src: 'icons/stroke-hide.svg' }, // TODO 1 use left inside Button (PasswordInput)
  { src: 'icons/stroke-hourglass.svg' },
  { src: 'icons/stroke-like.svg' }, // TODO 1 use left inside Button
  { src: 'icons/stroke-case.svg' },
  { src: 'icons/stroke-code.svg' },
  { src: 'icons/stroke-accessibility-eye.svg' },
  { src: 'icons/stroke-accessibility-ear.svg' },
  { src: 'icons/stroke-accessibility-leg.svg' },
  { src: 'icons/stroke-accessibility-brain.svg' },
  { src: 'icons/stroke-duplicate-offer.svg' },
  { src: 'icons/stroke-pie.svg' },
  { src: 'icons/stroke-new-offer.svg' },
  { src: 'icons/stroke-close.svg' },
  { src: 'icons/stroke-left.svg' },
  { src: 'icons/stroke-right.svg' },
  { src: 'icons/stroke-pass.svg' },
]

const shadowIcons: IconListItem[] = [
  { src: 'icons/shadow-tips-help.svg', viewBox: '0 0 22 26' },
  { src: 'icons/shadow-calendar.svg', viewBox: '0 0 24 24' },
]

const notCleandIcons: IconListItem[] = [
  // Not cleaned
  { src: 'icons/checkbox-check.svg', viewBox: '0 0 10 8' },
  { src: 'icons/checkbox.svg', viewBox: '0 0 10 8' },
  { src: 'icons/close-tag.svg', viewBox: '0 0 10 10' },
  { src: 'icons/ico-double-check.svg' },
  { src: 'icons/ico-eye-open-filled-black.svg' },
  { src: 'icons/fraud.svg', viewBox: '0 0 88 88' },
  { src: 'icons/ico-guichet-full.svg' },
  { src: 'icons/library.svg', viewBox: '0 0 49 48' },
  { src: 'icons/linear-gradient.svg', viewBox: '0 0 623 1024' }, // TODO replace by a jpg/png
  { src: 'icons/loader.svg', viewBox: '0 0 32 32' },
  { src: 'icons/location.svg', viewBox: '0 0 24 24' },
  { src: 'icons/logo-pass-culture.svg', viewBox: '0 0 114 84' },
  { src: 'icons/logo-pass-culture-header.svg', viewBox: '0 0 119 40' },
  { src: 'icons/logo-pass-culture-white.svg', viewBox: '0 0 282 120' },
  { src: 'icons/ico-no-bookings.svg', viewBox: '0 0 124 124' },
  { src: 'icons/ico-404.svg', viewBox: '0 0 308 194' },
  { src: 'icons/ico-notification-success.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-placeholder-offer-image.svg', viewBox: '0 0 80 80' },
  { src: 'icons/ico-offers.svg', viewBox: '0 0 48 49' },
  { src: 'icons/open-dropdown.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-other-download.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-other.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-radio-off.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-radio-on.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-search-gray.svg', viewBox: '0 0 124 125' },
  { src: 'icons/ico-separator.svg', viewBox: '0 0 20 1' },
  { src: 'icons/ico-signout.svg', viewBox: '0 0 48 49' },
  { src: 'icons/ico-star.svg', viewBox: '0 0 38 36' },
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
  { src: 'icons/ico-status-validated-white.svg', viewBox: '0 0 17 17' },
  { src: 'icons/ico-success.svg', viewBox: '0 0 88 88' },
  { src: 'icons/ico-tag.svg', viewBox: '0 0 33 33' },
  { src: 'icons/ticket-cross.svg', viewBox: '0 0 100 80' },
  { src: 'icons/ico-trash.svg' },
  { src: 'icons/ico-trophee.svg', viewBox: '0 0 24 25' },
  { src: 'icons/ico-unavailable-gradient.svg', viewBox: '0 0 178 100' },
  { src: 'icons/ico-unavailable-page.svg', viewBox: '0 0 317 198' },
  { src: 'icons/ico-unavailable-page-white.svg', viewBox: '0 0 317 198' },
  { src: 'icons/ico-warning.svg', viewBox: '0 0 16 16' },
  { src: 'icons/ico-subcategory.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-chevron-adage.svg', viewBox: '0 0 20 20' },
  { src: 'icons/add-user.svg', viewBox: '0 0 106 74' },
  { src: 'icons/ico-arrow-up-b.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-calendar-check.svg', viewBox: '0 0 48 48' },
  { src: 'icons/icon-calendar.svg', viewBox: '0 0 30 30' },
  { src: 'icons/ico-clock.svg', viewBox: '0 0 24 24' },
  { src: 'icons/ico-date.svg', viewBox: '0 0 48 48' },
  { src: 'icons/ico-disconnect-full.svg', viewBox: '0 0 40 40' },
  { src: 'icons/ico-key.svg', viewBox: '0 0 20 20' },
  { src: 'icons/logo-pass-culture-dark.svg', viewBox: '0 0 71 24' },
  { src: 'icons/offer-card-euro.svg', viewBox: '0 0 30 30' },
  { src: 'icons/other-offer.svg', viewBox: '0 0 30 30' },
  { src: 'icons/party.svg', viewBox: '0 0 48 48' },
  { src: 'icons/ico-search.svg', viewBox: '0 0 48 48' },
  { src: 'icons/ico-ticket-plus-full.svg', viewBox: '0 0 20 20' },
  { src: 'icons/ico-trash-filled.svg', viewBox: '0 0 48 48' },
  { src: 'icons/venue-2.svg', viewBox: '0 0 40 40' },
  { src: 'icons/ico-venue.svg', viewBox: '0 0 28 23' },
  { src: 'icons/ico-institution.svg', viewBox: '0 0 18 18' },
  { src: 'icons/logo-pass-culture-adage.svg', viewBox: '0 0 120 39' },
]

const iconsSections = [
  { title: 'Full icons', icons: fullIcons },
  { title: 'Stroke icons', icons: strokeIcons },
  { title: 'Shadow icons', icons: shadowIcons },
  { title: 'Not cleaned icons', icons: notCleandIcons },
]

export const Icons = () => {
  const [searchInput, setSearchInput] = useState('')
  const [fillColorInput, setFillColorInput] = useState('#000000')
  const [backgroundColorInput, setBackgroundColorInput] = useState('#ffffff')

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
    <div className={styles['icon-stories']}>
      <div className={styles['search-input-container']}>
        <BaseInput
          name="search"
          onChange={event => setSearchInput(event.target.value)}
          placeholder="Rechercher ..."
          value={searchInput}
        />

        <BaseInput
          type="color"
          name="fillColor"
          onChange={event => setFillColorInput(event.target.value)}
          placeholder="#000000, red...."
          value={fillColorInput}
          className={styles['color-input']}
        />

        <BaseInput
          type="color"
          name="backgroundColor"
          onChange={event => setBackgroundColorInput(event.target.value)}
          placeholder="#000000, red...."
          value={backgroundColorInput}
          className={styles['color-input']}
        />
      </div>

      {iconsSections.map(section => {
        const filteredIcons = section.icons.filter(iconListItem =>
          fuzzyMatch(searchInput, iconListItem.src)
        )

        if (filteredIcons.length === 0) {
          return null
        }

        return (
          <div key={section.title}>
            <Title level={2}>{section.title}</Title>

            <div className={styles['icon-list']}>
              {filteredIcons.map(icon => {
                const fileNameParts = icon.src.split('/')
                const iconName = fileNameParts[fileNameParts.length - 1]
                  .split('.')[0]
                  .replace('full-', '')
                  .replace('stroke-', '')
                  .replace('shadow-', '')

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
                        style={{
                          fill: fillColorInput,
                          color: fillColorInput,
                          backgroundColor: backgroundColorInput,
                        }}
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
      })}
    </div>
  )
}
