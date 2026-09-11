import { useId } from 'react'

import { ErrorLayout } from '@/app/App/layouts/ErrorLayout/ErrorLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import strokeErrorIcon from '@/icons/stroke-error.svg'

export const BackendVersionMismatch = () => {
  const reloadUrl = new URL(window.location.href)
  reloadUrl.searchParams.delete('_reload')
  const reloadPath = `${reloadUrl.pathname}${reloadUrl.search}${reloadUrl.hash}`
  const errorReturnLinkId = useId()

  return (
    <ErrorLayout
      mainHeading="Une mise à jour est disponible"
      paragraph="L'espace partenaire a été mis à jour. Cliquez ci-dessous pour continuer."
      errorIcon={strokeErrorIcon}
      cta={
        <Button
          as="router-link"
          id={errorReturnLinkId}
          variant={ButtonVariant.SECONDARY}
          to={reloadPath}
          onClick={(event) => {
            event.preventDefault()
            window.location.replace(reloadUrl.toString())
          }}
          label={'Mettre à jour'}
        />
      }
    />
  )
}
