import { connect } from 'react-redux'

import { showNotification } from 'store/reducers/notificationReducer'

import DownloadButton from './DownloadButton'

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { filename, href, mimeType } = ownProps

  return {
    downloadFileOrNotifyAnError: async () => {
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

        dispatch(
          showNotification({
            text: 'Il y a une erreur avec le chargement du fichier csv.',
            type: 'error',
          })
        )
      } catch (error) {
        console.log('error', error)
      }
    },
  }
}

export default connect(null, mapDispatchToProps)(DownloadButton)
