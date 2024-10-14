export const downloadFile = (data: Blob, filename: string) => {
  const fakeLink = document.createElement('a')

  fakeLink.href = URL.createObjectURL(data)
  fakeLink.setAttribute('download', filename)

  document.body.appendChild(fakeLink)
  fakeLink.click()
  document.body.removeChild(fakeLink)
}
