import {CheckHistory, UserBaseInfo} from "./types";
import {Card} from "@material-ui/core";
import {Button, Grid, Stack, Tooltip, Typography} from "@mui/material";
import Moment from "moment";
import React, {useState} from "react";
import {dataProvider} from "../../providers/dataProvider";
import {useNotify} from "react-admin";

export default function UserDetailsCard(user: UserBaseInfo, firstIdCheckHistory: CheckHistory) {
    const notify = useNotify();

    const [editable, setEditable] = useState(false)

    async function resendValidationEmail() {
        const response = await dataProvider.postResendValidationEmail('public_accounts', user)
        const responseData = await response.json()
        if (response.code !== 200) {
            notify(Object.values(responseData)[0] as string, {type: "error"})
        }
    }

    async function skipPhoneValidation() {
        const response = await dataProvider.postSkipPhoneValidation('public_accounts', user)
        let responseData;
        if (response.body) {
            responseData = await response.json()
        }
        if (response.code !== 204 && responseData) {
            notify(Object.values(responseData)[0] as string, {type: "error"})
        } else if (response.code === 204 || response.ok) {
            notify("Le numéro de téléphone a été confirmé avec succès", {type: "success"})
        }
    }

    async function sendPhoneValidationCode() {
        const response = await dataProvider.postPhoneValidationCode('public_accounts', user)
        const responseData = await response.json()
        if (response.code !== 200) {
            notify(Object.values(responseData)[0] as string, {type: "error"})
        } else if (response.code === 204) {
            notify("Un code a été envoyé au numéro de téléphone indiqué", {type: "success"})
        }
    }

    const cardStyle = {
        width: "100%",
        marginTop: "20px",
        padding: 30,
    }
    return (<>
        <Card style={cardStyle}>
            <Typography variant={"h5"}>
                Détails utilisateur
            </Typography>
            <Grid container spacing={1} sx={{mt: 4}}>
                <Stack spacing={3} direction={"row"} style={{width: "100%"}}>
                    <Grid item xs={4}>
                        <p>Nom</p>
                        <p>{user.lastName}</p>
                    </Grid>
                    <Grid item xs={4}>
                        <p>Prénom</p>
                        <p>{user.firstName}</p>
                    </Grid>
                    <Grid item xs={4}>
                        <p>Email</p>
                        {user.email && <>
                            <p>{user.email}</p>
                            <Button variant={"outlined"} onClick={resendValidationEmail}>Renvoyer l'email de
                                validation</Button>
                        </>}
                    </Grid>
                </Stack>
                <Stack spacing={3} direction={"row"} style={{width: "100%"}}>

                    <Grid item xs={4}>
                        <p>Numéro de téléphone</p>
                        <p>{user.phoneNumber ? user.phoneNumber : "N/A"}</p>
                        <Stack width={"60%"} spacing={2} textAlign={"left"}>
                            <Tooltip
                                title={!user.phoneNumber ? "Veuillez renseigner le numéro de téléphone" : ""}
                                arrow>
                                <div>
                                    <Button disabled={!user.phoneNumber} variant="outlined"
                                            onClick={sendPhoneValidationCode}>Envoyer un code de
                                        validation</Button>
                                </div>
                            </Tooltip>
                            <Tooltip
                                title={!user.phoneNumber ? "Veuillez renseigner le numéro de téléphone" : ""}>
                                <div>
                                    <Button disabled={!user.phoneNumber} variant="outlined"
                                            onClick={skipPhoneValidation}>Confirmer manuellement</Button>
                                </div>
                            </Tooltip>
                        </Stack>
                    </Grid>
                    <Grid item xs={4}>
                        <p>Date de naissance</p>
                        <p>{user.dateOfBirth ? Moment(user.dateOfBirth).format('D/MM/YYYY') : "N/A"}</p>
                    </Grid>
                    <Grid item xs={4}>
                        <p>Date de création du compte : </p>
                        <p>{firstIdCheckHistory && firstIdCheckHistory.dateCreated ? Moment(firstIdCheckHistory.dateCreated).format("D/MM/YYYY à HH:mm") : "N/A"}</p>
                    </Grid>
                </Stack>
                <Stack spacing={3} direction={"row"} style={{width: "100%"}}>

                    <Grid item xs={4}>
                        <p>N&deg; de la pièce d’identité</p>
                        <p>{firstIdCheckHistory && firstIdCheckHistory.technicalDetails && firstIdCheckHistory.technicalDetails.identificationId ? firstIdCheckHistory.technicalDetails.identificationId : "N/A"}</p>
                    </Grid>
                    <Grid item xs={3}>
                        <p>Adresse</p>
                        <p>{user.address}</p>
                    </Grid>
                    <Grid item xs={2}>
                        <p>CP</p>
                        <p>{user.postalCode}</p>
                    </Grid>
                    <Grid item xs={3}>
                        <p>Ville</p>
                        <p>{user.city}</p>
                    </Grid>
                </Stack>
            </Grid>
        </Card>
    </>)
}