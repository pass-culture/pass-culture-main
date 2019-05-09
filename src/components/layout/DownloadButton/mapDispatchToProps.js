import { showNotification } from 'pass-culture-shared'

const mapDispatchToProps = (dispatch, ownProps) => {
  const { fileType, href } = ownProps
  return {
    downloadFileOrNotifyAnError: async () => {
      try {
        const result = await fetch(href, { credentials: 'include' })
        const { ok } = result

        if (ok) {
          const text = await result.text()
          const blob = new Blob([text], { type: fileType })
          window.location.href = window.URL.createObjectURL(blob)
          return
        }

        dispatch(
          showNotification({
            text: 'Il y a une erreur avec le chargement du fichier csv.',
            type: 'danger',
          })
        )
      } catch (error) {
        console.log('error', error)
      }
    },
  }
}

export default mapDispatchToProps
