import React, { useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import { Button } from 'ui-kit'

interface IDownloadButtonProps {
  filename: string
  href: string
  mimeType: string
  children: React.ReactNode | React.ReactNode[]
  isDisabled: boolean
}

const ButtonDownloadCSV = ({
  filename,
  href,
  mimeType,
  children,
  isDisabled,
}: IDownloadButtonProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const downloadFileOrNotifyAnError = async () => {
    try {
      const result = await fetch(href, { credentials: 'include' })
      const { status } = result

      if (status === 200) {
        const text = await result.text()
        const fakeLink = document.createElement('a')
        const blob = new Blob([text], { type: mimeType })
        const date = new Date().toISOString()

        // Ce n'est pas terrible mais nous n'avons pas trouvé mieux.
        // Aucun code d'avant ne faisait que l'on téléchargeait un fichier
        // avec l'extension CSV.
        fakeLink.href = URL.createObjectURL(blob)
        fakeLink.setAttribute('download', `${filename}-${date}.csv`)
        document.body.appendChild(fakeLink)
        fakeLink.click()
        document.body.removeChild(fakeLink)

        return
      }
    } catch (error) {
      // Nothing to do
    }

    notification.error('Il y a une erreur avec le chargement du fichier csv.')
  }

  const handleOnClick = async () => {
    setIsLoading(true)
    await downloadFileOrNotifyAnError()
    setIsLoading(false)
  }

  return (
    <Button
      disabled={isLoading || isDisabled}
      onClick={handleOnClick}
      type="button"
    >
      {children}
    </Button>
  )
}

export default ButtonDownloadCSV
