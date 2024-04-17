import React, { useState } from 'react'

import useNotification from 'hooks/useNotification'
import { Button } from 'ui-kit'
import { downloadFile } from 'utils/downloadFile'

export interface DownloadButtonProps {
  filename: string
  href: string
  mimeType: string
  children: React.ReactNode | React.ReactNode[]
  isDisabled: boolean
}

export const ButtonDownloadCSV = ({
  filename,
  href,
  mimeType,
  children,
  isDisabled,
}: DownloadButtonProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const downloadFileOrNotifyAnError = async () => {
    try {
      const result = await fetch(href, { credentials: 'include' })
      const { status } = result

      if (status === 200) {
        const text = await result.text()

        const date = new Date().toISOString()
        downloadFile(text, `${filename}-${date}.csv`, mimeType)

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
