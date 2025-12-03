import style from './AccessibleDate.module.scss'

type AccessibleDateProps = {
  date: Date | string
  visualOptions?: Intl.DateTimeFormatOptions
}

export function AccessibleDate({ date, visualOptions }: AccessibleDateProps) {
  const d = date instanceof Date ? date : new Date(date)
  const spoken = new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(d)
  const visual = new Intl.DateTimeFormat('fr-FR', visualOptions).format(d)
  const machineReadable = d.toISOString().split('T')[0]

  return (
    <time dateTime={machineReadable}>
      {/* This version is for visual users.
       */}
      <span aria-hidden="true">{visual}</span>

      {/*
        This version is for screen readers.
        The "sr-only" class hides it from visual users.
      */}
      <span className={style['sr-only']}>{spoken}</span>
    </time>
  )
}
