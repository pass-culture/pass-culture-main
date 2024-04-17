export const downloadFile = (
  data: BlobPart,
  filename: string,
  mimeType: string
) => {
  const fakeLink = document.createElement('a')
  const blob = new Blob([data], {
    type: mimeType,
  })

  fakeLink.href = URL.createObjectURL(blob)
  fakeLink.setAttribute('download', filename)

  document.body.appendChild(fakeLink)
  fakeLink.click()
  document.body.removeChild(fakeLink)
}
