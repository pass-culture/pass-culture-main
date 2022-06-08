import * as React from 'react';
import {Box, Button, Typography, Modal, Grid, Select, MenuItem, TextField} from "@mui/material"
import {useState} from "react";
import {Form, SelectField, SaveButton, SimpleForm, Identifier} from 'react-admin';
import {FieldValues} from "react-hook-form";
import {dataProvider} from "../../providers/dataProvider";
import {useForm} from "react-hook-form";
import SendIcon from '@mui/icons-material/Send';
import {UserManualReview} from "./types";


export default function ManualReviewModal(userId: any) {
    const [openModal, setOpenModal] = useState(false)
    const {register, handleSubmit} = useForm();

    const styleModal = {
        position: 'absolute' as 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 800,
        height: 600,
        bgcolor: 'background.paper',
        border: '1px solid #000',
        boxShadow: 24,
        p: 4,
    };
    const handleOpenModal = () => setOpenModal(true)
    const handleCloseModal = () => setOpenModal(false)

    const formSubmit = async (params: FieldValues) => {
        console.log(userId, params)
        if (params && userId) {
            try {
                const formData : UserManualReview = {
                    id: userId.userId,
                    review: params.review,
                    reason : params.reason,
                    eligibility: params.eligibility
                }
                const response = await dataProvider.postUserManualReview('public_accounts/user', formData)
                if (response && response.statusCode == 200) {
                    alert("La revue a été envoyée avec succès !")
                    handleCloseModal()
                }
            } catch (e) {
                return Promise.reject(e)
            }
        }
    }

    return (
        <>
            <Button  variant={"contained"} onClick={handleOpenModal}>Revue manuelle</Button>
            <Modal
                open={openModal}
                onClose={handleCloseModal}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
            >
                <Box sx={styleModal}>
                    <form onSubmit={handleSubmit((data) => formSubmit(data))}>

                        <Select {...register("review")} fullWidth label={"Revue"}>
                            <MenuItem value=""></MenuItem>
                            <MenuItem value={"ok"}>OK</MenuItem>
                            <MenuItem value={"ko"}>KO</MenuItem>
                            <MenuItem value={"redirected_to_dms"}>Renvoi vers DMS</MenuItem>
                        </Select>

                        <Select {...register("eligibility")} label={"Eligibilité"} fullWidth
                                placeholder={'Eligibilité'}>
                            <MenuItem value={""}>Par Défaut</MenuItem>
                            <MenuItem value={"underage"}>Pass 15-17</MenuItem>
                            <MenuItem value={"age18"}>Pass 18 ans</MenuItem>
                        </Select>
                        <TextField {...register("reason")} multiline rows={4} placeholder="Raison" fullWidth/>
                        <Button type={"submit"} variant="contained" endIcon={<SendIcon/>}>Valider</Button>
                    </form>
                </Box>
            </Modal>
        </>
    );
}