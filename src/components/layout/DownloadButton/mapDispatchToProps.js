import { showNotification } from 'pass-culture-shared'

const mapDispatchToProps = (dispatch, ownProps) => {
  const { fileType, href } = ownProps

  return {
    downloadFileOrNotifyAnError: async () => {
      try {
        const result = await fetch(href, { credentials: 'include' })
        const { status } = result

        if (status === 200) {
          const text = await result.text()
          const fakeLink = document.createElement('a')
          const blob = new Blob([text], { type: fileType })
          const date = new Date().toISOString()
          let filename = 'remboursements_pass_culture'

          // Ce n'est pas terrible mais nous n'avons pas trouvé mieux.
          // Aucun code d'avant ne faisait que l'on téléchargeait un fichier
          // avec l'extension CSV.
          // Pour le nom des fichiers, je n'ai pas réussi à le récupérer dans
          // l'entête du fetch donc si on modifie ici, faut modifier côté API
          // aussi (bookings.py et reimbursements.py).
          if (href.includes('bookings')) {
            filename = 'reservations_pass_culture_pass_culture'
          }
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
