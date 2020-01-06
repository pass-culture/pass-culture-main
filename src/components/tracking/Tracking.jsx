const Traking = () => {
  if (window.location.href === 'https://app.passculture.beta.gouv.fr/beta') {
    window.snaptr('track', 'PAGE_VIEW')
    window.fbq('track', 'PageView')
  }

  return null
}

export default Traking
