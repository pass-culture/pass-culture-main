import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

export const MarkdownInfoBox = () => {
  return (
    <InfoBox>
      Vous pouvez modifier la mise en forme de votre texte.
      <br />
      Utilisez des doubles astérisques pour mettre en{' '}
      <strong>gras</strong> : **exemple** et des tirets bas pour l’
      <em>italique</em> : _exemple_
      <br />
      Vous pourrez vérifier l’affichage à l’étape "Aperçu".
    </InfoBox>
  )
}