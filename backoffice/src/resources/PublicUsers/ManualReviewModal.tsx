import * as React from 'react';
import {Box, Button, Modal} from "@mui/material"
import {useState} from "react";
import {Form, SelectInput, useNotify, TextInput, SaveButton} from 'react-admin';
import {FieldValues} from "react-hook-form";
import {dataProvider} from "../../providers/dataProvider";
import {UserManualReview} from "./types";


export default function ManualReviewModal(userId: any) {
    const [openModal, setOpenModal] = useState(false)
    const notify = useNotify();

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
                const formData: UserManualReview = {
                    id: userId.userId,
                    review: params.review,
                    reason: params.reason,
                    eligibility: params.eligibility
                }
                const response = await dataProvider.postUserManualReview('public_accounts/user', formData)
                const data = await response.json()
                if (response && response.status == 200) {
                    notify("La revue a été envoyée avec succès !", {type: "success"})
                    handleCloseModal()
                } else if (response && (response.status == 412 || response.status == 500)) {
                    notify(JSON.stringify(data.global), {type: "error"})
                    handleCloseModal()
                }
            } catch (e) {
                return Promise.reject(e)
            }
        }
    }

    return (
        <>
            <Button variant={"contained"} onClick={handleOpenModal}>Revue manuelle</Button>
            <Modal
                open={openModal}
                onClose={handleCloseModal}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
            >
                <Box sx={styleModal}>
                    <Form onSubmit={formSubmit}>
                        <SelectInput source="review" label={"Revue"} emptyValue={null} fullWidth choices={[
                            {id: 'OK', name: 'OK'},
                            {id: 'KO', name: 'KO'},
                            {id: 'REDIRECTED_TO_DMS', name: 'Renvoi vers DMS'},
                        ]}/>
                        <SelectInput source="eligibility" label={"Éligibilité"} fullWidth choices={[
                            {id: '', name: 'Par Défaut'},
                            {id: 'UNDERAGE', name: 'Pass 15-17'},
                            {id: 'AGE18', name: 'Pass 18 ans'},
                        ]}/>
                        <TextInput label="Raison" source="reason" fullWidth multiline rows={4}/>
                        <SaveButton label={"Confirmer"}/>
                    </Form>
                </Box>
            </Modal>
        </>
    );
}