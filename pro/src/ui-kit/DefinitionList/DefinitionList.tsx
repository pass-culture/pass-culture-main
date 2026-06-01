import type { PropsWithChildren } from 'react'

import style from './DefinitionList.module.scss'

/**
 * @see https://adrianroselli.com/2025/01/updated-brief-note-on-description-list-support.html (W3C Accessibility Expert)
 * @see https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dl#accessibility
 */
const _DefinitionList = ({ children }: Readonly<PropsWithChildren>) => {
  return <dl className={style['list']}>{children}</dl>
}

const Row = ({ children }: Readonly<PropsWithChildren>) => (
  <div className={style['row']}>{children}</div>
)

const Term = ({ children }: Readonly<PropsWithChildren>) => (
  <dt className={style['term']}>{children} : </dt>
)

const Definition = ({ children }: Readonly<PropsWithChildren>) => (
  <dd className={style['definition']}>{children}</dd>
)

export const DefinitionList = Object.assign(_DefinitionList, {
  Definition,
  Row,
  Term,
})
