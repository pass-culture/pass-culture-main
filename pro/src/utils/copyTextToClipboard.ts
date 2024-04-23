export const copyTextToClipboard = async (text: string) => {
  if ('clipboard' in navigator) {
    await navigator.clipboard.writeText(text)
  } else {
    document.execCommand('copy', true, text)
  }
}
