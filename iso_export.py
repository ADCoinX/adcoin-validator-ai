
from datetime import datetime

def generate_iso_xml(wallet, network, balance):
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Document>
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>ADC-{wallet}</MsgId>
      <CreDtTm>{now}</CreDtTm>
    </GrpHdr>
    <PmtInf>
      <Dbtr>
        <Nm>{wallet}</Nm>
      </Dbtr>
      <Cdtr>
        <Nm>ADC Validator System</Nm>
      </Cdtr>
      <Amt Ccy="{network}">{balance}</Amt>
      <RmtInf>
        <Ustrd>Wallet Risk Validation Report</Ustrd>
      </RmtInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>"""
