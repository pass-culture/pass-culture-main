import typing

from . import activity
from . import base
from . import digital
from . import unselectable


DIGITAL = {
    unselectable.CaptationMusiqueModel,
    digital.AboJeuVideoModel,
    digital.AboLivreNumeriqueModel,
    digital.AboPlateformeMusiqueModel,
    digital.AboPlateformeVideoModel,
    digital.AboPresseEnLigneModel,
    digital.AppCulturelleModel,
    digital.AutreSupportNumeriqueModel,
    digital.JeuEnLigneModel,
    digital.LivreNumeriqueModel,
    digital.PlateformePratiqueArtistiqueModel,
    digital.PodcastModel,
    digital.SpectacleEnregistreModel,
    digital.TelechargementLivreAudioModel,
    digital.TelechargementMusiqueModel,
    digital.VODModel,
    digital.VisiteVirtuelleModel,
    activity.LivestreamEvenementModel,
    activity.LivestreamMusiqueModel,
    activity.LivestreamPratiqueArtistiqueModel,
}


ACTIVITY = {
    unselectable.ActivationEventModel,
    unselectable.DecouverteMetiersModel,
    activity.AtelierPratiqueArtModel,
    activity.CinePleinAirModel,
    activity.ConcertModel,
    activity.ConcoursModel,
    activity.ConferenceModel,
    activity.EvenementCineModel,
    activity.EvenementJeuModel,
    activity.EvenementMusiqueModel,
    activity.EvenementPatrimoineModel,
    activity.FestivalArtVisuelModel,
    activity.FestivalCineModel,
    activity.FestivalLivreModel,
    activity.FestivalMusiqueModel,
    activity.FestivalSpectacleModel,
    activity.LivestreamEvenementModel,
    activity.LivestreamMusiqueModel,
    activity.LivestreamPratiqueArtistiqueModel,
    activity.RencontreEnLigneModel,
    activity.RencontreJeuModel,
    activity.RencontreModel,
    activity.SalonModel,
    activity.SeanceCineModel,
    activity.SeanceEssaiPratiqueArtModel,
    activity.SpectacleRepresentationModel,
    activity.VisiteGuideeModel,
    activity.VisiteLibreModel,
}


CANNOT_BE_CREATED = {
    unselectable.AboLudothequeModel,
    unselectable.ActivationEventModel,
    unselectable.ActivationThingModel,
    unselectable.BonAchatInstrumentModel,
    unselectable.CaptationMusiqueModel,
    unselectable.DecouverteMetiersModel,
    unselectable.JeuSupportPhysiqueModel,
    unselectable.OeuvreArtModel,
}


def is_digital(model: type[base.Base]) -> bool:
    return model in DIGITAL


def is_activity(model: type[base.Base]) -> bool:
    return model in ACTIVITY


def cannot_be_created(model: type[base.Base]) -> bool:
    return model in CANNOT_BE_CREATED


Typology = list[typing.Literal["digital", "activity", "unselectable"]]


def get_typology(model: type[base.Base]) -> Typology:
    typology: Typology = []

    if is_digital(model):
        typology.append("digital")
    if is_activity(model):
        typology.append("activity")
    if cannot_be_created(model):
        typology.append("unselectable")

    return typology
