import cn from 'classnames'
import { ReactElement } from 'react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDoubleCheckIcon from 'icons/stroke-double-check.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import strokeHourglassIcon from 'icons/stroke-hourglass.svg'
import strokeThing from 'icons/stroke-thing.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import style from './CollectiveStatusLabel.module.scss'

type CollectiveStatusLabelProps = {
  offerDisplayedStatus: CollectiveOfferDisplayedStatus
}

export const CollectiveStatusLabel = ({
  offerDisplayedStatus,
}: CollectiveStatusLabelProps) => {
  switch (offerDisplayedStatus) {
    case CollectiveOfferDisplayedStatus.UNDER_REVIEW:
      return (
        <StatusLabel
          className={style['status-pending']}
          icon={
            <SvgIcon
              className={cn(style['status-label-icon'])}
              src={strokeClockIcon}
              alt=""
            />
          }
          label="en instruction"
        />
      )
    case CollectiveOfferDisplayedStatus.REJECTED:
      return (
        <StatusLabel
          className={style['status-rejected']}
          icon={
            <SvgIcon
              alt=""
              src={strokeCloseIcon}
              className={style['status-label-icon']}
            />
          }
          label="non conforme"
        />
      )
    case CollectiveOfferDisplayedStatus.HIDDEN:
      return (
        <StatusLabel
          className={style['status-inactive']}
          icon={
            <SvgIcon
              alt=""
              src={fullHideIcon}
              className={style['status-label-icon']}
            />
          }
          label="en pause"
        />
      )
    case CollectiveOfferDisplayedStatus.PUBLISHED:
      return (
        <StatusLabel
          className={style['status-active']}
          icon={
            <SvgIcon
              src={strokeCheckIcon}
              alt=""
              className={style['status-label-icon']}
            />
          }
          label="publiée"
        />
      )
    case CollectiveOfferDisplayedStatus.PREBOOKED:
      return (
        <StatusLabel
          className={style['status-pre-booked']}
          icon={
            <SvgIcon
              className={cn(
                style['status-label-icon'],
                style['status-pre-booked-icon']
              )}
              src={strokeHourglassIcon}
              alt=""
            />
          }
          label="préréservée"
        />
      )
    case CollectiveOfferDisplayedStatus.BOOKED:
      return (
        <StatusLabel
          className={style['status-booked']}
          icon={
            <SvgIcon
              src={strokeClockIcon}
              alt=""
              className={style['status-label-icon']}
            />
          }
          label="réservée"
        />
      )
    case CollectiveOfferDisplayedStatus.EXPIRED:
      return (
        <StatusLabel
          className={style['status-expired']}
          icon={
            <SvgIcon
              alt=""
              src={strokeCalendarIcon}
              className={style['status-label-icon']}
            />
          }
          label="expirée"
        />
      )
    case CollectiveOfferDisplayedStatus.REIMBURSED:
      return (
        <StatusLabel
          className={style['status-reimbursed']}
          icon={
            <SvgIcon
              alt=""
              src={strokeEuroIcon}
              className={style['status-label-icon']}
            />
          }
          label="remboursée"
        />
      )
    case CollectiveOfferDisplayedStatus.ENDED:
      return (
        <StatusLabel
          className={style['status-ended']}
          icon={
            <SvgIcon
              alt=""
              src={strokeDoubleCheckIcon}
              className={style['status-label-icon']}
            />
          }
          label="terminée"
        />
      )
    case CollectiveOfferDisplayedStatus.CANCELLED:
      return (
        <StatusLabel
          className={style['status-cancelled']}
          icon={
            <SvgIcon
              src={strokeWrongIcon}
              alt=""
              className={style['status-label-icon']}
            />
          }
          label="annulée"
        />
      )
    case CollectiveOfferDisplayedStatus.ARCHIVED:
      return (
        <StatusLabel
          className={style['status-archived']}
          icon={
            <SvgIcon
              alt=""
              src={strokeThing}
              className={style['status-label-icon']}
            />
          }
          label="archivée"
        />
      )
    case CollectiveOfferDisplayedStatus.DRAFT:
      return (
        <StatusLabel
          className={style['status-draft']}
          icon={
            <SvgIcon
              alt=""
              src={strokeThing}
              className={cn(
                style['status-label-icon'],
                style['status-draft-icon']
              )}
            />
          }
          label="brouillon"
        />
      )
  }
}

type StatusLabelProps = {
  className: string
  icon: ReactElement
  label: string
}

const StatusLabel = ({ className, icon, label }: StatusLabelProps) => {
  return (
    <span className={cn(style['status-label'], className)}>
      <>
        {icon}
        {label}
      </>
    </span>
  )
}
