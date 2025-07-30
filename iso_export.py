from datetime import datetime

def generate_iso_xml(wallet_address):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>ADC-{wallet_address[:6]}</MsgId>
      <CreDtTm>{now}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>0</CtrlSum>
      <InitgPty>
        <Nm>ADC CryptoGuard</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>Payment-{wallet_address[:6]}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <BtchBookg>false</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <CtrlSum>0</CtrlSum>
      <PmtTpInf>
        <InstrPrty>NORM</InstrPrty>
        <SvcLvl>
          <Cd>SEPA</Cd>
        </SvcLvl>
      </PmtTpInf>
      <ReqdExctnDt>{now[:10]}</ReqdExctnDt>
      <Dbtr>
        <Nm>{wallet_address}</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>{wallet_address}</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BIC>ADCOINMYKL</BIC>
        </FinInstnId>
      </DbtrAgt>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>TX-{wallet_address[:8]}</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="USD">0.00</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId>
            <BIC>ADCOINMYKL</BIC>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>Blockchain Wallet</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <Othr>
              <Id>{wallet_address}</Id>
            </Othr>
          </Id>
        </CdtrAcct>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>"""

    return xml_template
