VALID_TRANSACTION = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>passCulture-SCT-20181015-114356</MsgId>
            <CreDtTm>2018-10-15T09:21:34</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>30</CtrlSum>
            <InitgPty>
                <Nm>pass Culture</Nm>
                <Id>
                    <OrgId>
                        <Othr>
                            <Id>0000</Id>
                        </Othr>
                    </OrgId>
                </Id>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>passCulture-SCT-20181015-114356</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>30</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
                <CtgyPurp>
                    <Cd>GOVT</Cd>
                </CtgyPurp>
            </PmtTpInf>
            <ReqdExctnDt>2018-10-22</ReqdExctnDt>
            <Dbtr>
                <Nm>pass Culture</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>BD12AZERTY123456</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BIC>AZERTY9Q666</BIC>
                </FinInstnId>
            </DbtrAgt>
            <ChrgBr>SLEV</ChrgBr>

            <CdtTrfTxInf>
                <PmtId>
                    <EndToEndId>ff1920dc2883458d9f290c9e70d2418d</EndToEndId>
                </PmtId>
                <Amt>
                    <InstdAmt Ccy="EUR">30</InstdAmt>
                </Amt>
                <UltmtDbtr>
                    <Nm>pass Culture</Nm>
                </UltmtDbtr>
                <CdtrAgt>
                    <FinInstnId>
                        <BIC>QSDFGH8Z555</BIC>
                    </FinInstnId>
                </CdtrAgt>
                <Cdtr>
                    <Nm>Test Offerer</Nm>
                    <Id>
                        <OrgId>
                            <Othr>
                                <Id>123456789</Id>
                            </Othr>
                        </OrgId>
                    </Id>
                </Cdtr>
                <CdtrAcct>
                    <Id>
                        <IBAN>CF13QSDFGH456789</IBAN>
                    </Id>
                </CdtrAcct>
                <Purp>
                    <Cd>GOVT</Cd>
                </Purp>
                <RmtInf>
                    <Ustrd>pass Culture Pro - remboursement 2nde quinzaine 07-2018</Ustrd>
                </RmtInf>
            </CdtTrfTxInf>

        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>
"""

INVALID_TRANSACTION = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <CstmrCdtTrfInitn>
        <!-- missing GrpHdr -->
        <PmtInf>
            <PmtInfId>passCulture-SCT-20181015-114356</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>30</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
                <CtgyPurp>
                    <Cd>GOVT</Cd>
                </CtgyPurp>
            </PmtTpInf>
            <ReqdExctnDt>2018-10-22</ReqdExctnDt>
            <Dbtr>
                <Nm>pass Culture</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>BD12AZERTY123456</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BIC>AZERTY9Q666</BIC>
                </FinInstnId>
            </DbtrAgt>
            <ChrgBr>SLEV</ChrgBr>
            <!-- Missing CdtTrfTxInf -->
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>
"""

VALID_TRANSACTION_WITH_MALFORMED_XML_DECLARATION = """

<!-- illegal blank lines at beginning of file -->

<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>passCulture-SCT-20181015-114356</MsgId>
            <CreDtTm>2018-10-15T09:21:34</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>30</CtrlSum>
            <InitgPty>
                <Nm>pass Culture</Nm>
                <Id>
                    <OrgId>
                        <Othr>
                            <Id>0000</Id>
                        </Othr>
                    </OrgId>
                </Id>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>passCulture-SCT-20181015-114356</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>30</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
                <CtgyPurp>
                    <Cd>GOVT</Cd>
                </CtgyPurp>
            </PmtTpInf>
            <ReqdExctnDt>2018-10-22</ReqdExctnDt>
            <Dbtr>
                <Nm>pass Culture</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <IBAN>BD12AZERTY123456</IBAN>
                </Id>
            </DbtrAcct>
            <DbtrAgt>
                <FinInstnId>
                    <BIC>AZERTY9Q666</BIC>
                </FinInstnId>
            </DbtrAgt>
            <ChrgBr>SLEV</ChrgBr>

            <CdtTrfTxInf>
                <PmtId>
                    <EndToEndId>ff1920dc2883458d9f290c9e70d2418d</EndToEndId>
                </PmtId>
                <Amt>
                    <InstdAmt Ccy="EUR">30</InstdAmt>
                </Amt>
                <UltmtDbtr>
                    <Nm>pass Culture</Nm>
                </UltmtDbtr>
                <CdtrAgt>
                    <FinInstnId>
                        <BIC>QSDFGH8Z555</BIC>
                    </FinInstnId>
                </CdtrAgt>
                <Cdtr>
                    <Nm>Test Offerer</Nm>
                    <Id>
                        <OrgId>
                            <Othr>
                                <Id>123456789</Id>
                            </Othr>
                        </OrgId>
                    </Id>
                </Cdtr>
                <CdtrAcct>
                    <Id>
                        <IBAN>CF13QSDFGH456789</IBAN>
                    </Id>
                </CdtrAcct>
                <Purp>
                    <Cd>GOVT</Cd>
                </Purp>
                <RmtInf>
                    <Ustrd>pass Culture Pro - remboursement 2nde quinzaine 07-2018</Ustrd>
                </RmtInf>
            </CdtTrfTxInf>

        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>
"""